from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import  Supplier
from reviews.models import Review

@receiver(post_save, sender=Review)
def update_supplier_rating_on_save(sender, instance, **kwargs):
    if instance.supplier:
        instance.supplier.update_rating()
    if instance.delivery:
        instance.delivery.update_rating()

@receiver(post_delete, sender=Review)
def update_supplier_rating_on_delete(sender, instance, **kwargs):
    if instance.supplier:
        instance.supplier.update_rating()
    if instance.delivery:
        instance.delivery.update_rating()