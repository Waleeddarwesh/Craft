from django.contrib import admin
from .models import ReturnRequest, DeliveryReturnRequest, Balance_Withdraw_Request, transactions

class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order', 'product', 'quantity', 'status', 'amount', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at', 'amount')
    search_fields = ('user__username', 'order__id', 'product__name', 'confirmation_code', 'stripe_id')
    readonly_fields = ('id', 'confirmation_code', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'order', 'product', 'quantity', 'status', 'initial_status', 'amount', 'stripe_id')
        }),
        ('Delivery Details', {
            'fields': ('delivery', 'from_state', 'to_state', 'to_address', 'from_address', 'related_order', 'confirmation_code', 'delivery_confirmed_at')
        }),
    )

class DeliveryReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'delivery_person', 'ReturnRequest', 'accepted_at')
    list_filter = ('accepted_at',)
    search_fields = ('delivery_person__username', 'ReturnRequest__id')
    readonly_fields = ('id', 'accepted_at')

class Balance_Withdraw_RequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'transfer_number', 'transfer_type', 'transfer_status', 'amount', 'notes')
    list_filter = ('transfer_type', 'transfer_status')
    search_fields = ('user__username', 'transfer_number')
    readonly_fields = ('id',)

class TransactionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'transaction_type')
    readonly_fields = ('id', 'created_at')

admin.site.register(ReturnRequest, ReturnRequestAdmin)
admin.site.register(DeliveryReturnRequest, DeliveryReturnRequestAdmin)
admin.site.register(Balance_Withdraw_Request, Balance_Withdraw_RequestAdmin)
admin.site.register(transactions, TransactionsAdmin)