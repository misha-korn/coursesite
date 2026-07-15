from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'course', 'student', 'amount', 'status', 'external_id', 'created_at']
        read_only_fields = ['student', 'amount', 'status', 'external_id', 'created_at']