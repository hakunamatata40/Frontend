# payments/models.py
from django.db import models
from django.conf import settings
from courses.models import Course

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=5, default='usd') # e.g., 'usd', 'xaf'
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True, unique=True) # Stripe Charge ID
    status = models.CharField(max_length=50, default='pending') # e.g., 'pending', 'succeeded', 'failed', 'refunded'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Transaction {self.stripe_charge_id or "N/A"} for {self.user.username} - {self.status}'