from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "invoice",
            "amount",
            "payment_date",
            "payment_method",
            "note",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]

    def create(self, validated_data):
        invoice = validated_data["invoice"]
        user = invoice.user

        payment = Payment.objects.create(
            user=user,
            **validated_data
        )

        return payment
