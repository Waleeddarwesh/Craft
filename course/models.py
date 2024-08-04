from django.db import models
from accounts.models import Supplier, Customer
from products.models import Category
from django.core.validators import MaxValueValidator, MinValueValidator

class Course(models.Model):
    CourseID = models.AutoField(primary_key=True)
    Thumbnail = models.ImageField(upload_to='course_thumbnails/%Y/%m/%d', blank=True, null=True)
    CourseTitle = models.CharField(max_length=100)
    CategoryID = models.ForeignKey(Category, on_delete=models.CASCADE)
    Rating =  models.DecimalField(max_digits=10, decimal_places=2,default= 5.0,validators=(MinValueValidator(0.0), MaxValueValidator(5.0))) 
    completed = models.BooleanField(default=False)
    NumberOfRatings = models.IntegerField(default=0)
    FromDate = models.DateTimeField(blank=True, null=True)
    ToDate = models.DateTimeField(blank=True, null=True)
    CourseHours = models.IntegerField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    NumberOfLec = models.IntegerField(default=0,blank=True, null=True)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Description = models.TextField()
    Supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, blank=True,null=True,related_name='sub')
    
    def __str__(self):
        return f"{self.CourseTitle}"

    def update_rating(self):
        avg_rating = self.course_rating.aggregate(models.Avg('rating'))['rating__avg']
        self.Rating = avg_rating if avg_rating is not None else 0
        self.save()
    
class CourseVideos(models.Model):
    VideoID = models.AutoField(primary_key=True)
    CourseID = models.ForeignKey(Course, on_delete=models.CASCADE)
    LectureTitle = models.CharField(max_length=100)
    VideoNo = models.IntegerField()
    Description = models.TextField()
    VideoFile = models.FileField(upload_to='videos/%y/%m/%d')

    def __str__(self):
        return f"{self.LectureTitle}"

class Enrollment(models.Model):
    EnrollmentID = models.AutoField(primary_key=True)
    Course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='enrollments')
    EnrollmentDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enrollment ID: {self.EnrollmentID}, Course: {self.Course.CourseTitle}"