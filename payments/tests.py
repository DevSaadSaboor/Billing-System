from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient

from customers.models import Customer
from invoices.models import Invoice, InvoiceLineItem
from payments.models import Payment
from datetime import timedelta


class PaymentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.customer = Customer.objects.create(
            user=self.user,
            name="Test Customer",
            email="test@example.com"
        )
    def test_partial_payment_allowed(self):
        invoice = Invoice.objects.create(
        user=self.user,
        customer=self.customer,
        invoice_number="INV-PARTIAL",
        issue_date=timezone.now(),
        due_date=timezone.now() + timedelta(days=10),
        status="draft"
    )

        InvoiceLineItem.objects.create(
        invoice=invoice,
        description="Service",
        quantity=1,
        unit_price=1000,
        tax_rate=0
    )

    # Send invoice
        self.client.post(f"/api/invoices/{invoice.id}/send/")

    # Make partial payment
        response = self.client.post("/api/payments/", {
        "invoice": invoice.id,
        "amount": 500,
        "payment_date": "2026-02-22",
        "payment_method": "cash"
    })

        invoice.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(invoice.status, "sent")
    
    
    
    def test_full_payment_marks_invoice_as_paid(self):
        from datetime import timedelta

        invoice = Invoice.objects.create(
        user=self.user,
        customer=self.customer,
        invoice_number="INV-FULL-PAY",
        issue_date=timezone.now(),
        due_date=timezone.now() + timedelta(days=10),
        status="draft"
    )

        InvoiceLineItem.objects.create(
        invoice=invoice,
        description="Service",
        quantity=1,
        unit_price=1000,
        tax_rate=0
    )

    # Send invoice
        self.client.post(f"/api/invoices/{invoice.id}/send/")

    # Make full payment
        response = self.client.post("/api/payments/", {
        "invoice": invoice.id,
        "amount": 1000,
        "payment_date": "2026-02-22",
        "payment_method": "cash"
    })

        invoice.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(invoice.status, "paid")