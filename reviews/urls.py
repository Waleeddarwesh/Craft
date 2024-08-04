from django.urls import path
from .views import *
urlpatterns = [
    
    path('product/', ProductReviewCreate.as_view(), name='product-review-create'),
    path('product/<int:pk>/', ProductReviewUpdateDelete.as_view(), name='product-review-update-delete'),
    path('product-reviews/<int:product_id>/', ProductReviewList.as_view(), name='product-review-list'),
    path('course/', CourseReviewCreate.as_view(), name='course-review-create'),
    path('course/<int:pk>/', CourseReviewUpdateDelete.as_view(), name='course-review-update-delete'),
    path('course-reviews/<int:course_id>/', CourseReviewList.as_view(), name='course-review-list'),
    path('delivery/', DeliveryReviewCreate.as_view(), name='delivery-review-create'),
    path('delivery/<int:pk>/', DeliveryReviewUpdateDelete.as_view(), name='delivery-review-update-delete'),
    path('delivery-reviews/<int:delivery_id>/', DeliveryReviewList.as_view(), name='delivery-review-list'),
    path('supplier/', SupplierReviewCreate.as_view(), name='supplier-review-create'),
    path('supplier/<int:pk>/', SupplierReviewUpdateDelete.as_view(), name='supplier-review-update-delete'),
    path('supplier-reviews/<int:supplier_id>/', SupplierReviewList.as_view(), name='supplier-review-list'),
    
]
