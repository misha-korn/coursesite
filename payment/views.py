from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Payment
from payment.serializators import PaymentSerializer
from payment.services import create_provider_payment, handle_payment_succeeded


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
        event = request.data.get("event")
        obj = request.data.get("object", {})
        external_id = obj.get("id")

        if event == "payment.succeeded" and external_id is not None:
            handle_payment_succeeded(external_id)

        return Response(status=status.HTTP_200_OK)
