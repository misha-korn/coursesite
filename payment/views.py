import logging
import os

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Payment
from payment.serializators import PaymentSerializer
from payment.services import create_provider_payment, handle_payment_succeeded, is_yookassa_ip

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
            handle_payment_succeeded(external_id)

        return Response(status=status.HTTP_200_OK)
