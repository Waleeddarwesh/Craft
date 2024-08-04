from django.db import models
from products.models import Product
from course.models import Course
from accounts.models import Customer,Delivery,Supplier

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    delivery_choices = (
        ('Dissatisfied',1),
        ('Satisfied',2),
        ('Very Satisfied',3)
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_rating', on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey(Course,related_name='course_rating', on_delete=models.CASCADE, null=True, blank=True)
    delivery = models.ForeignKey(Delivery,related_name='delivery_rating', on_delete=models.CASCADE, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, related_name='supplier_rating',on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    image = models.ImageField(upload_to="product_reviews_images/%y/%m/%d", default="", null=True, blank=True)
    ease_of_place_order = models.CharField(choices = delivery_choices, null=True, blank=True , max_length=50)
    speed_of_delivery = models.CharField(choices = delivery_choices, null=True, blank=True, max_length=50)
    product_packaging =  models.CharField(choices = delivery_choices, null=True, blank=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)