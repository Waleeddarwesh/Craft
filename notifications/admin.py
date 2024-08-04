from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class Notification(admin.ModelAdmin):
    list_display = ("message", "is_read", "timestamp")
    list_filter = ("is_read", "timestamp")
    search_fields = ("message",)
    readonly_fields = ("timestamp",)
    fieldsets = (
        (None, {"fields": ("message", "is_read")}),
        ("Date Information", {"fields": ("timestamp",), "classes": ("collapse",)}),
    )
    ordering = ("-timestamp",)
    actions = ["mark_as_sent"]

    @admin.action(description="Mark selected notifications as sent")
    def mark_as_sent(self, request, queryset):
     queryset.update(sent=True)