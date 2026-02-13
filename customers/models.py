from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="customers"
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=50, blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"