from django.db import models
from accounts.models import User
from orders.models import Order
# Create your models here.

class PaymentHistory(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    order=models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    date=models.DateTimeField(auto_now_add=True)
    payment_status=models.BooleanField()

    def __str__(self):
        return self.order.user