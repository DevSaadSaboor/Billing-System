from rest_framework import serializers
from .models import Invoice,InvoiceLineItem
from django.db.models import Sum
from django.db import transaction
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError



class InvoiceLineItemSerializer(serializers.ModelSerializer):
    class Meta:
     
        model = InvoiceLineItem
        fields = [
            "id",
            "description",
            "quantity",
            "unit_price",
            "tax_rate",
            "line_subtotal",
            "line_tax",
            "line_total",
        ]
        read_only_fields = [
            "id",
            "line_subtotal",
            "line_tax",
            "line_total",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    line_items = InvoiceLineItemSerializer(many=True)
    total_paid = serializers.SerializerMethodField()
    remaining_balance = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "customer",
            "invoice_number",
            "issue_date",
            "due_date",
            "status",
            "subtotal",
            "tax_total",
            "grand_total",
            "note",
            "created_at",
            "total_paid",
            "remaining_balance",
            "line_items",
        ]
        read_only_fields = [
            "id",
            "subtotal",
            "tax_total",
            "grand_total",
            "created_at",
        ]


    def create(self, validated_data):
        line_items_data = validated_data.pop("line_items", [])

        customer = validated_data["customer"]
        user = customer.user

        try:
            invoice = Invoice.objects.create(
            user=user,
            **validated_data
        )
        except IntegrityError:
            raise ValidationError(
            {"invoice_number": "Invoice number must be unique per user."}
        )

    # Create line items
        for item_data in line_items_data:
            InvoiceLineItem.objects.create(
            invoice=invoice,
            **item_data
        )

    # Recalculate totals
        invoice.recalculate_totals()

        return invoice

    def get_total_paid(self,obj):
        result = obj.payments.aggregate(total = Sum("amount"))
        return result["total"] or 0     
    
    def get_remaining_balance(self,obj):
        result = obj.payments.aggregate(total = Sum("amount"))
        total_paid  = result["total"] or  0
        return obj.grand_total - total_paid
    

  