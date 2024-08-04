from django.contrib import admin
from .models import PaymentHistory

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'date', 'payment_status')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'order__id')
    list_filter = ('payment_status', 'date')
    ordering = ('-date',)