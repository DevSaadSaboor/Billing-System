from rest_framework import serializers
from .models import Invoice,InvoiceLineItem

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

        # get customer and its user
        customer = validated_data["customer"]
        user = customer.user

        # create invoice with user
        invoice = Invoice.objects.create(
            user=user,
            **validated_data
        )

        # create line items
        for item_data in line_items_data:
            InvoiceLineItem.objects.create(
                invoice=invoice,
                **item_data
            )

        # recalculate totals
        invoice.recalculate_totals()
        return invoice
