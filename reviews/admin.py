from django.contrib import admin
from .models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'course', 'delivery', 'supplier', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('customer__username', 'product__name', 'course__title', 'delivery__id', 'supplier__name')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('customer', 'product', 'course', 'delivery', 'supplier', 'rating', 'comment', 'image')
        }),
        ('Delivery Ratings', {
            'fields': ('ease_of_place_order', 'speed_of_delivery', 'product_packaging')
        }),
    )

admin.site.register(Review, ReviewAdmin)
