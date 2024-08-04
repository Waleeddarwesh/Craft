from django.db import models
from accounts.models import Supplier
from django.utils.text import slugify
from accounts .models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models import Avg

class Category(models.Model):
    CategoryID = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=100)
    Description = models.TextField()
    Picture = models.ImageField(upload_to='category_images/%y/%m/%d', blank=True, null=True)
    Active = models.BooleanField(default=True)
    Slug = models.SlugField(null=True,blank=True, unique=True)

    def __str__(self):
        return self.Title
    
class MatCategory(models.Model):
    MatID = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=100)
    Picture = models.ImageField(upload_to='category_images/%y/%m/%d', blank=True, null=True)
    Active = models.BooleanField(default=True)
    Slug = models.SlugField(null=True,blank=True, unique=True)
    def save(self, *args, **kwargs):
        if not self.Slug:
         self.Slug=slugify(self.Title)
         super(MatCategory,self).save(*args,**kwargs)

    def __str__(self):
        return self.Title
    
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    ProductName = models.CharField(max_length=100)
    ProductDescription = models.TextField()
    MatCategory = models.ForeignKey(MatCategory, on_delete=models.CASCADE,blank=True, null=True,related_name = "MatCatPro")
    Category = models.ForeignKey(Category, on_delete=models.CASCADE,blank=True, null=True,related_name = "CatPro")
    Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    QuantityPerUnit = models.CharField(max_length=50)
    UnitPrice = models.DecimalField(max_digits=10, decimal_places=2)
    UnitWeight = models.DecimalField(max_digits=5, decimal_places=2)
    Stock = models.IntegerField(null=False,blank=False)
    OutOfStock = models.BooleanField(default=False)
    DiscountAvailable = models.BooleanField(default=False)
    Discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    DiscountPercentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    Rating = models.DecimalField(max_digits=10, decimal_places=2,default= 5.0,validators=(MinValueValidator(0.0), MaxValueValidator(5.0)))
    Publish_Date = models.DateTimeField(auto_now_add=True) 
    width = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True,validators=(MinValueValidator(0.0), MaxValueValidator(1000.0)))
    height = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True,validators=(MinValueValidator(0.0), MaxValueValidator(1000.0)))
    watt = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True,validators=(MinValueValidator(0.0), MaxValueValidator(1000.0)))
    
    def __str__(self):
        return self.ProductName

    def update_rating(self):
        avg_rating = self.product_rating.aggregate(Avg('rating'))['rating__avg']
        self.Rating = avg_rating if avg_rating is not None else 0
        self.save()

    def save(self, *args, **kwargs):
        if self.DiscountPercentage > 0:
            self.Discount = (self.UnitPrice * self.DiscountPercentage) / 100
            self.UnitPrice = (self.UnitPrice - self.Discount)

        else:
            self.Discount = 0.0
        super().save(*args, **kwargs)
        
@receiver(pre_save, sender=Product)
def toggle_out_of_stock(sender, instance, **kwargs):
    if instance.Stock == 0:
        instance.OutOfStock = True
    else:
        instance.OutOfStock = False    
               
class ProImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name = "images")
    image = models.ImageField(upload_to="product_images/%y/%m/%d", default="", null=True, blank=True)
    
    def __str__(self):
        return self.product.ProductName

class ProColors(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name = "Colors")
    Color = models.CharField(max_length=20,blank=True, null=True) 

    def __str__(self):
        return self.product.ProductName
    
class ProSizes(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name = "Sizes")
    Size = models.CharField(max_length=20,blank=True, null=True) 

    def __str__(self):
        return self.product.ProductName

class Collection(models.Model):
    supplier = models.ForeignKey(Supplier, related_name='collections', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class CollectionItem(models.Model):
    collection = models.ForeignKey(Collection, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='collection_items', on_delete=models.CASCADE)
