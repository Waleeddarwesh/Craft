import random
import string
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.db import models
from products.models import Product
from accounts.models import User,Address,Supplier,Delivery
import uuid
from django.contrib.auth import get_user_model
from django.db import models
from products.models import Product
from django.utils.crypto import get_random_string

class Wishlist(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist for: {self.user.get_full_name}"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')

    def __str__(self):
        return f"Wishlist Item: {self.product.ProductName}"

class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    User = models.OneToOneField(User, on_delete=models.CASCADE)
    Created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
 
    def _str_(self):
        return f"Cart ID: {self.User.get_full_name()}"

class CartItems(models.Model):
    CartID = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name="items", null=True, blank=True)
    Product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='cartitems',null=True, blank=True)
    Quantity = models.PositiveIntegerField()
    
    def _str_(self):
        return f"Cart Item: {self.Product.ProductName}"
    
User = get_user_model()
class Order(models.Model):
    class OrderStatus(models.TextChoices):
        CREATED = 'created'
        PAID='paid'
        ON_MY_WAY = 'on my way'
        DELIVERED_TO_First_WAREHOUSE = 'delivered to First warehouse'
        In_Transmit='In Transmit'
        DELIVERED_TO_Second_WAREHOUSE = 'delivered to Second warehouse'
        DELIVERED_SUCCESSFULLY = 'delivered successfully'
        FAILED_DELIVERY = 'failed delivery'
        CANCELLED = 'cancelled'
    
    class PaymentMethod(models.TextChoices):
        CASH_ON_DELIVERY = 'Cash on Delivery '
        CREDIT_CARD='Credit Card'
        BALANCE = 'Balance'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
    delivery = models.ForeignKey(Delivery,on_delete=models.CASCADE,null=True)
    supplier = models.ForeignKey(Supplier,on_delete=models.CASCADE,related_name="Supplier_orders",null=True)
    from_state = models.CharField(max_length=250, blank=True)
    to_state = models.CharField(max_length=250, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="orders",null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE )
    from_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="order_supplier_address", null=True, blank=True)
    related_order = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='related_orders',default=None)
    confirmation_code = models.CharField(max_length=6, null=True, blank=True)
    delivery_confirmed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=OrderStatus.choices, default=OrderStatus.CREATED)
    initial_status = models.CharField(max_length=50, choices=OrderStatus.choices, default=OrderStatus.CREATED)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    delivery_fee =  models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_method = models.CharField(max_length=50, choices=PaymentMethod.choices, default=PaymentMethod.CASH_ON_DELIVERY)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.confirmation_code :
            self.confirmation_code = ''.join(random.choices(string.digits, k=4))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "created_at"])]

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
      
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OrderItem {self.product.ProductName} by {self.order.user}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["order", "product"])]

    def get_cost(self):
        return self.price * self.quantity
    
class Coupon(models.Model):
    supplier = models.ForeignKey(Supplier, related_name='coupons', on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    terms = models.TextField()
    products = models.ManyToManyField(Product, related_name='coupons')

    def __str__(self):
        return self.code    

class DeliveryOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    delivery_person = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_orders')
    order = models.ForeignKey(Order, related_name='delivery_orders', on_delete=models.CASCADE,null=True)
    accepted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.delivery_person} accepted {self.order}" 

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    Address = models.ForeignKey(Address,on_delete=models.CASCADE)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    delivery_fee= models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name