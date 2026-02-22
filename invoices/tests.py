from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from invoices.models import InvoiceLineItem
from customers.models import Customer
from invoices.models import Invoice


class InvoiceTests(TestCase):

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        # Create API client
        self.client = APIClient()

    def test_authenticated_user_can_access_invoice_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/invoices/")
        self.assertEqual(response.status_code, 200)


    def test_unauthenticated_user_cannot_access_invoice_list(self):
        response = self.client.get("/api/invoices/")
        self.assertEqual(response.status_code, 401)


    def test_cannot_send_invoice_without_line_items(self):
        self.client.force_authenticate(user=self.user)

        customer = Customer.objects.create(
        user=self.user,
        name="Test Customer",
        email="test@example.com"
    )

        invoice = Invoice.objects.create(
        user=self.user,
        customer=customer,
        invoice_number="INV-NO-LINES",
        issue_date=timezone.now(),
        due_date=timezone.now(),
        status="draft"
    )
        response = self.client.post(f"/api/invoices/{invoice.id}/send/")
        invoice.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(invoice.status, "draft")


    def test_draft_invoice_can_be_sent(self):
        self.client.force_authenticate(user=self.user)
        customer = Customer.objects.create(
            user=self.user,
            name="Test Customer",
            email="test@example.com"
        )

        invoice = Invoice.objects.create(
            user=self.user,
            customer=customer,
            invoice_number="INV-TEST-1",
            issue_date=timezone.now(),
            due_date=timezone.now(),
            status="draft",
            subtotal=100,
            tax_total=0,
            grand_total=100
        )
        InvoiceLineItem.objects.create(
        invoice=invoice,
        description="Test Service",
        quantity=1,
        unit_price=100,
        tax_rate=0
        )
        
        response = self.client.post(f"/api/invoices/{invoice.id}/send/")
        invoice.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(invoice.status, "sent")
    

    def test_cannot_resend_sent_invoice(self):
        self.client.force_authenticate(user=self.user)
        customer = Customer.objects.create(
        user=self.user,
        name="Test Customer",
        email="test@example.com"
    )

        invoice = Invoice.objects.create(
        user=self.user,
        customer=customer,
        invoice_number="INV-RESEND",
        issue_date=timezone.now(),
        due_date=timezone.now(),
        status="draft"
    )

        InvoiceLineItem.objects.create(
        invoice=invoice,
        description="Test Service",
        quantity=1,
        unit_price=100,
        tax_rate=0
    )

    # First send (should succeed)
        first_response = self.client.post(f"/api/invoices/{invoice.id}/send/")
        self.assertEqual(first_response.status_code, 200)

    # Second send (should fail)
        second_response = self.client.post(f"/api/invoices/{invoice.id}/send/")

        invoice.refresh_from_db()

    # Assertions
        self.assertEqual(second_response.status_code, 400)
        self.assertEqual(invoice.status, "sent")


