from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "course", "student", "amount", "status", "external_id", "created_at"]
        read_only_fields = ["student", "amount", "status", "external_id", "created_at"]

    def validate(self, data):
        course = data.get("course")
        payments = Payment.objects.filter(
            student=self.context["request"].user,
            course=course,
            status=Payment.Status.SUCCEEDED
        )
        if payments.exists():
            raise serializers.ValidationError("Вы уже оплатили этот курс")
        if course.author == self.context["request"].user:
            raise serializers.ValidationError("Нельзя купить свой курс")
        return data