from django.contrib import admin
from django.urls import path
from rest_framework import routers
from django.conf.urls import include
from .views import *

router=routers.DefaultRouter()
router.register('products',ProductsViewSet)
router.register('collections', CollectionViewSet, basename='collection')

urlpatterns = [
    
    path('',include(router.urls)),
    path('productsByFollowedSuppliers/',FollowedSuppliersProducts.as_view(),name='productsByFollowedSuppliers'),
    path('ProductsByCategory/<slug:Slug>/',ProductsByCategory.as_view()),
    path('categories/',Categories.as_view()),
    path('Materials/',Mataterials.as_view()),
    path('ProductsByMaterials/<slug:Slug>/',ProductsByMaterials.as_view()),
    path('uploadImage/', ImageUploadView.as_view(), name='upload_image'),

]
