# payments/admin.py
from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount', 'currency', 'status', 'created_at', 'stripe_charge_id']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['user__username', 'course__title', 'stripe_charge_id']
    readonly_fields = ['user', 'course', 'amount', 'currency', 'stripe_charge_id', 'created_at', 'updated_at']