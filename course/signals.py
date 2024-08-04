from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from reviews.models import Review 
from .models import Course

@receiver(post_save, sender=Review)
def update_related_rating_on_save(sender, instance, **kwargs):
    if instance.course:
        instance.course.update_rating()

@receiver(post_delete, sender=Review)
def update_related_rating_on_delete(sender, instance, **kwargs):
    if instance.course:
        instance.course.update_rating()

