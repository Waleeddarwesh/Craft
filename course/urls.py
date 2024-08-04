from django.urls import path,include
from .views import  CourseAPIView, LectureListCreateAPIView,LectureRetrieveUpdateDestroyAPIView,CourseLecturesAPIView,SimpleCoursesListAPIView,OneCourseDetailView,EnrolledCoursesAPIView
from rest_framework import routers

router=routers.DefaultRouter()
router.register('courses', CourseAPIView, basename='course-create')
router.register('course-detail', OneCourseDetailView, basename='course-detail')
urlpatterns = [
    path('',include(router.urls)),
    path('courses-list/', SimpleCoursesListAPIView.as_view(), name='all-courses-list'),
    path('lecture/', LectureListCreateAPIView.as_view(), name='lecture-create'),
    path('lecture/<int:pk>/', LectureRetrieveUpdateDestroyAPIView.as_view(), name='lecture-retrieve-update-destroy'),
    path('user/courses/', EnrolledCoursesAPIView.as_view(), name='user-courses-list'),
    path('course-lectures/<int:CourseID>/', CourseLecturesAPIView.as_view(), name='course-lectures'),

]

