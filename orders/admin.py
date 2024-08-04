from django.contrib import admin
from .models import Wishlist, WishlistItem, Cart, CartItems, Order, OrderItem, Coupon, DeliveryOrder, Warehouse

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'Created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-Created_at',)

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('wishlist', 'product')
    search_fields = ('wishlist__user__email', 'wishlist__user__first_name', 'wishlist__user__last_name', 'product__ProductName')
    list_filter = ('wishlist__Created_at',)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('User', 'Created_at')
    search_fields = ('User__email', 'User__first_name', 'User__last_name')
    ordering = ('-Created_at',)

@admin.register(CartItems)
class CartItemsAdmin(admin.ModelAdmin):
    list_display = ('CartID', 'Product', 'Quantity')
    search_fields = ('CartID__User__email', 'CartID__User__first_name', 'CartID__User__last_name', 'Product__ProductName')
    list_filter = ('CartID__Created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'total_amount', 'paid')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'product__ProductName')
    list_filter = ('status', 'created_at', 'paid')
    ordering = ('-created_at',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'created_at')
    search_fields = ('order__user__email', 'order__user__first_name', 'order__user__last_name', 'product__ProductName')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'supplier', 'discount', 'valid_from', 'valid_to', 'active')
    search_fields = ('code', 'supplier__user__email', 'supplier__user__first_name', 'supplier__user__last_name')
    list_filter = ('active', 'valid_from', 'valid_to')
    ordering = ('-valid_from',)

@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    list_display = ('delivery_person', 'order', 'accepted_at')
    search_fields = ('delivery_person__email', 'delivery_person__first_name', 'delivery_person__last_name', 'order__id')
    list_filter = ('accepted_at',)
    ordering = ('-accepted_at',)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'Address', 'contact_person', 'contact_phone', 'delivery_fee')
    search_fields = ('name', 'contact_person', 'contact_phone')
    ordering = ('name',)
