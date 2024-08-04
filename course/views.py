from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import generics,status,permissions,serializers,viewsets
from rest_framework.generics import RetrieveAPIView
from .serializers import CourseSerializer,CourseVideosSerializer,SimpleCoursesSerializer
from .models import Course, CourseVideos,Enrollment,Customer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsSupplier,IsCustomer,IsSupplierOrCustomer
from rest_framework.exceptions import PermissionDenied,ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.http import Http404

class CourseAPIView(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsSupplier]

    def perform_create(self, serializer):
        supplier_instance = self.request.user.supplier
        course_name = serializer.validated_data.get('CourseTitle')
        existing_course = Course.objects.filter(CourseTitle=course_name).exists()
        if not existing_course:
            serializer.save(Supplier=supplier_instance)
        else:
            raise serializers.ValidationError("Course with this name already exists")
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": "Course created successfully"}, status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_update(self, serializer):
        course = serializer.instance
        if course.Supplier.user != self.request.user:
            raise PermissionDenied("You are not allowed to edit this course.")
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.Supplier.user != self.request.user:
            raise PermissionDenied("You are not allowed to delete this course.")
        instance.delete()

class LectureListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CourseVideosSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        CourseID = self.request.query_params.get('CourseID')
        if not CourseID:
            raise Http404("CourseID not provided.")
        
        if not Course.objects.filter(id=CourseID).exists():
            raise Http404("Course not found.")

        return CourseVideos.objects.filter(CourseID=CourseID)

    def perform_create(self, serializer):
        course = serializer.validated_data['CourseID']
        if course.Supplier.user != self.request.user:
            raise PermissionDenied("You are not allowed to create videos for this course.")
        serializer.save()

class LectureRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CourseVideos.objects.all()
    serializer_class = CourseVideosSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_permission(self, instance):
        if instance.CourseID.Supplier.user != self.request.user:
            raise PermissionDenied("You are not allowed to perform this action on this video.")

    def perform_update(self, serializer):
        instance = serializer.instance
        self.check_permission(instance)
        serializer.save()

    def perform_destroy(self, instance):
        self.check_permission(instance)
        instance.delete()

class SimpleCoursesListAPIView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = SimpleCoursesSerializer
    permission_classes = [permissions.IsAuthenticated]

class OneCourseDetailView(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated,IsCustomer]
   
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseSerializer
        return self.serializer_class
    
    def get_permissions(self):
        if self.action == 'retrieve':
            return [IsAuthenticated(), IsCustomer()]
        elif self.action in ['create','update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSupplier()]  
        return [IsAuthenticated()]  
    
class CourseLecturesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            raise PermissionDenied("Course not found.")

        user = request.user
        if hasattr(user, 'customer'):
            customer = user.Customer
            if not Enrollment.objects.filter(Course=course, Customer=customer).exists():
                raise PermissionDenied("You are not allowed to access this course.")
        else:
            raise PermissionDenied("You are not allowed to access this course.")

        serializer = CourseSerializer(course)
        return Response(serializer.data)

class EnrolledCoursesAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_customer:
            try:
                customer = user.customer
                enrollments = Enrollment.objects.filter(Customer=customer)
                courses = [enrollment.Course for enrollment in enrollments]
                serializer = CourseSerializer(courses, many=True)
                return Response(serializer.data)
            except Customer.DoesNotExist:
                return Response({"detail": "Customer profile does not exist."}, status=404)
        
        elif user.is_supplier:
            
            return Response({"detail": " Supplier Can't ُ Enroll Courses "}, status=501)
        
        else:
            return Response({"detail": " User does not have appropriate profile."}, status=403)
