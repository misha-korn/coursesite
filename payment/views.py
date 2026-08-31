import logging
import os

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import BalanceEntry, Payment, Payout, PayoutMethod
from payment.serializators import (
    BalanceEntrySerializer,
    PaymentSerializer,
    PayoutMethodSerializer,
    PayoutSerializer,
)
from payment.services import (
    create_provider_payment,
    get_balance,
    is_yookassa_ip,
    request_payout,
    set_default_payout_method,
    verify_payout_method,
)
from payment.tasks import handle_payment_succeeded

logger = logging.getLogger("payment.views")

YOOKASSA_ENABLED = os.environ.get("YOOKASSA_ENABLED") == "1"


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR")


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentSerializer
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return Payment.objects.filter(student=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.validated_data["course"]
        payment = serializer.save(
            student=self.request.user,
            amount=course.price,
        )
        url = create_provider_payment(payment)
        return Response({"payment_url": url}, status=status.HTTP_201_CREATED)


class YookassaWebhookView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        ip = get_client_ip(request)
        logger.info("Вебхук оплаты по ip %s: %s", ip, request.data)

        if YOOKASSA_ENABLED and not is_yookassa_ip(ip):
            logger.warning("Вебхук с постороннего ip %s отклонен", ip)
            return Response(status=status.HTTP_403_FORBIDDEN)

        event = request.data.get("event")
        obj = request.data.get("object", {})
        external_id = obj.get("id")

        if event == "payment.succeeded" and external_id is not None:
            handle_payment_succeeded.delay(external_id)

        return Response(status=status.HTTP_200_OK)


class PayoutViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    serializer_class = PayoutSerializer

    def get_queryset(self):
        return Payout.objects.filter(author=self.request.user).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payout = request_payout(self.request.user, serializer.validated_data["amount"])

        return Response(self.get_serializer(payout).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def balance(self, request):
        return Response({"balance": get_balance(request.user.id)})


class BalanceEntryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = BalanceEntrySerializer

    def get_queryset(self):
        return BalanceEntry.objects.filter(author=self.request.user).order_by("-created_at")


class PayoutMethodViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    serializer_class = PayoutMethodSerializer

    def get_queryset(self):
        return PayoutMethod.objects.filter(author=self.request.user, is_active=True).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        method = serializer.save(author=self.request.user)
        verify_payout_method(method)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.is_default = False
        instance.save(update_fields=["is_active", "is_default"])

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        method = set_default_payout_method(pk, request.user)
        return Response(self.get_serializer(method).data, status=status.HTTP_200_OK)
