from rest_framework import serializers

from payment.models import BalanceEntry, Payment, Payout


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "course", "student", "amount", "status", "external_id", "created_at"]
        read_only_fields = ["student", "amount", "status", "external_id", "created_at"]

    def validate(self, data):
        course = data.get("course")
        payments = Payment.objects.filter(
            student=self.context["request"].user, course=course, status=Payment.Status.SUCCEEDED
        )
        if payments.exists():
            raise serializers.ValidationError("Вы уже оплатили этот курс")
        if course.author == self.context["request"].user:
            raise serializers.ValidationError("Нельзя купить свой курс")
        return data


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = [
            "id",
            "author",
            "amount",
            "status",
            "external_id",
            "created_at",
            "updated_at",
            "paid_at",
        ]
        read_only_fields = ["author", "status", "external_id", "created_at", "updated_at"]


class BalanceEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceEntry
        fields = ["id", "author", "kind", "payment", "payout", "comment", "created_at"]
        read_only_fields = fields
