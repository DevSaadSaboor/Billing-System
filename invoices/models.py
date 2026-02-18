from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer
from django.utils import timezone


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="invoices"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="invoices"
    )

    invoice_number = models.CharField(max_length=50)
    issue_date = models.DateTimeField()
    due_date = models.DateTimeField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def recalculate_totals(self):
         items = self.line_items.all()

         subtotal = sum(item.line_subtotal for item in items)
         tax_total = sum(item.line_tax for item in items)
         grand_total = sum(item.line_total for item in items)

         self.subtotal = subtotal
         self.tax_total = tax_total
         self.grand_total = grand_total
         self.save(update_fields=['subtotal', 'tax_total', 'grand_total'])

    def update_status_from_payments(self):
        payments = self.payments.all()
        total_paid = sum(payment.amount for payment in payments)

        if total_paid >= self.grand_total and self.grand_total > 0:
            self.status = "paid"

        else:
            if self.due_date and self.due_date < timezone.now():
                self.status = "overdue"
            else:
                self.status = "send"

        self.save(update_fields=["status"]) 
            
    def update_overdue_status(self):
        if self.status != 'paid' and self.due_date < timezone.now():
            self.status = 'overdue'
            self.save(update_fields=["status"])


    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.name}"


class InvoiceLineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="line_items"
    )
    description = models.TextField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    line_subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    line_tax = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def save(self,*args,**kwargs):
        self.line_subtotal = self.quantity * self.unit_price
        self.line_tax = self.line_subtotal * (self.tax_rate /100)
        self.line_total = self.line_subtotal + self.line_tax
        
        super().save(*args,**kwargs)
        self.invoice.recalculate_totals()


    def delete(self,*args,**kwargs):
        invoice = self.invoice
        super().delete(*args,**kwargs)
        invoice.recalculate_totals()


    def __str__(self):
        return f"{self.description} (Invoice {self.invoice.invoice_number})"


