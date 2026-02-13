from django.db import models
from django.contrib.auth.models import User
from invoices.models import Invoice


from django.db import models
from django.contrib.auth.models import User
from invoices.models import Invoice


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank_transfer", "Bank Transfer"),
        ("card", "Card"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self,*args, **kwargs):
        super().save(*args,**kwargs)
        self.invoice.update_status_from_payments()

    def delete(self,*args,**kwargs):
        super().delete(*args,**kwargs)
        self.invoice.update_status_from_payments()
    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_number}"


