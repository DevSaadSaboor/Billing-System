from rest_framework import serializers
from .models import Payment
from rest_framework.exceptions import ValidationError
from django.db.models import Sum
from django.db import transaction



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

    # def validate(self,attrs):
    #     invoice = attrs.get("invoice")
    #     amount = attrs.get("amount")
    #     if not invoice or not amount:
    #         return attrs
    #     total_paid = sum(payment.amount for payment in invoice.payments.all())
    #     if total_paid + amount > invoice.grand_total:
    #         raise ValidationError("Payment amount exceeds invoice total.")        
    #     return attrs


    def create(self, validated_data):
        with transaction.atomic():
            invoice = validated_data["invoice"]

        # Lock the invoice row to prevent race conditions
        invoice = (
            invoice.__class__.objects
            .select_for_update()
            .get(pk=invoice.pk)
        )

        # Recalculate total paid safely inside transaction
        total_paid = invoice.payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        amount = validated_data["amount"]

        if total_paid + amount > invoice.grand_total:
            raise serializers.ValidationError(
                "Payment amount exceeds invoice total."
            )

        payment = Payment.objects.create(
            user=invoice.user,
            **validated_data
        )

        # Update invoice status after payment
        invoice.update_status_from_payments()

        return payment
       
   