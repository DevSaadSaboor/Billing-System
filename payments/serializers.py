from rest_framework import serializers
from .models import Payment
from rest_framework.exceptions import ValidationError


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

    def validate(self,attrs):
        invoice = attrs.get("invoice")
        amount = attrs.get("amount")
        if not invoice or not amount:
            return attrs
        total_paid = sum(payment.amount for payment in invoice.payments.all())
        if total_paid + amount > invoice.grand_total:
            raise ValidationError("Payment amount exceeds invoice total.")        
        return attrs


    def create(self, validated_data):
        invoice = validated_data["invoice"]
        user = invoice.user
        payment = Payment.objects.create(
            user=user,
            **validated_data
        )

        return payment

       
   