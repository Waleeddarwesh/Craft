from django.contrib import admin
from .models import Course, CourseVideos, Enrollment

class CourseAdmin(admin.ModelAdmin):
    list_display = ('CourseTitle', 'CategoryID', 'Rating', 'completed', 'FromDate', 'ToDate', 'Price', 'Supplier')
    search_fields = ('CourseTitle', 'CategoryID__title', 'Supplier__user__first_name', 'Supplier__user__last_name')
    list_filter = ('CategoryID', 'Rating', 'completed', 'FromDate', 'ToDate')
    ordering = ('-Rating',)

class CourseVideosAdmin(admin.ModelAdmin):
    list_display = ('LectureTitle', 'CourseID', 'VideoNo')
    search_fields = ('LectureTitle', 'CourseID__CourseTitle')
    list_filter = ('CourseID',)
    ordering = ('CourseID', 'VideoNo')

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('Course', 'Customer', 'EnrollmentDate')
    search_fields = ('Course__CourseTitle', 'Customer__user__first_name', 'Customer__user__last_name')
    list_filter = ('Course', 'EnrollmentDate')
    ordering = ('-EnrollmentDate',)

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseVideos, CourseVideosAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
