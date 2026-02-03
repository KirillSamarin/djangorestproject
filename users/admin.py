from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "payment_sum", "payment_method"]
    search_fields = ["user", "payment_sum", "payment_method"]
