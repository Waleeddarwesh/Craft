from django.contrib import admin
from .models import User, Customer, Supplier, Delivery, Address, Follow, OneTimePassword

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'is_verified')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'is_verified', 'is_customer', 'is_supplier', 'is_delivery')
    ordering = ('email',)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'CreditCardNO', 'CreditCardType')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_filter = ('CreditCardType',)

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('user', 'CategoryTitle', 'Rating', 'Orders', 'FollowersNo')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'CategoryTitle')
    list_filter = ('CategoryTitle', 'Rating')
    ordering = ('-Rating',)

class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('user', 'VehicleModel', 'VehicleColor', 'plateNO', 'Rating', 'Orders', 'ExperienceYears')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'VehicleModel', 'plateNO')
    list_filter = ('Rating', 'ExperienceYears')
    ordering = ('-Rating',)

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'BuildingNO', 'Street', 'City', 'State')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'Street', 'City', 'State')
    list_filter = ('City', 'State')

class FollowAdmin(admin.ModelAdmin):
    list_display = ('Customer', 'Supplier')
    search_fields = ('Customer__user__email', 'Customer__user__first_name', 'Customer__user__last_name',
                     'Supplier__user__email', 'Supplier__user__first_name', 'Supplier__user__last_name')
    list_filter = ('Customer', 'Supplier')

class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'otp')

admin.site.register(User, UserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Delivery, DeliveryAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(OneTimePassword, OneTimePasswordAdmin)
