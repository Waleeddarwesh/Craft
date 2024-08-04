from rest_framework import serializers
from .models import Course, CourseVideos, Enrollment
from orders.serializers import AddressSerializer
from accounts.serializers import CraftersSerializer

class SimpleCoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['CourseID','Thumbnail','CourseTitle','CategoryID','Rating','NumberOfRatings','FromDate','address','Price','completed']

class CourseSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=False,read_only=True)
    Supplier = CraftersSerializer(many=False,read_only=True)
    class Meta:
        model = Course
        fields = ['CourseID','Thumbnail',
                  'CourseTitle','CategoryID',
                  'Rating','completed',
                  'NumberOfRatings','FromDate',
                  'ToDate','CourseHours',
                  'address','NumberOfLec',
                  'Price','Description','Supplier']

class CourseVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseVideos
        fields = ['CourseID','VideoID','VideoNo','LectureTitle','VideoFile']

class EnrollmentSerializer(serializers.ModelSerializer):
    VideoFile = CourseVideosSerializer(many=True, read_only=True)
    class Meta:
        model = Enrollment
        fields = '__all__'