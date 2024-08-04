from django.contrib import admin
from .views import RegisterViewforcustomer,VerifyUserEmail,RegisterViewforSupplier,RegisterViewforDelivery,SupplierProfileAPIView
from .views import LoginUserView,PasswordResetRequestView,SetNewPasswordView,LogoutApiView,GoogleOauthSignInview
from . views import CustomerProfileAPIView, DeliveryProfileAPIView,SuppliersList,SupplierDetail,FollowSupplier,TrendingSuppliersAPIView,AddressViewSet,SupplierDocumentViewSet
from .views import deliveryDocumentViewSet
from django.urls import path , include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('addresses', AddressViewSet, basename='address')
router.register('supplier-documents', SupplierDocumentViewSet, basename='supplier-documents')
router.register('delivery-documents', deliveryDocumentViewSet, basename='supplier-documents')

urlpatterns = [
    path('register_customer/', RegisterViewforcustomer.as_view(), name='register_customer'),
    path('register_Supplier/', RegisterViewforSupplier.as_view(), name='register_Supplier'),
    path('register_delivery/', RegisterViewforDelivery.as_view(), name='register_delivery'),
    path('auth-google/', GoogleOauthSignInview.as_view(), name='auth-google'),
    path('verify_email/', VerifyUserEmail.as_view(), name='verify_email'),
    path('login/',LoginUserView.as_view(), name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    path('lohttp://10.0.2.2:8000/accounts/password-reset/gout/', LogoutApiView.as_view(), name='logout'),
    path('supplier/profile/', SupplierProfileAPIView.as_view(), name='supplier-profile'),
    path('customer/profile/', CustomerProfileAPIView.as_view(), name='customer-profile'),
    path('delivery/profile/', DeliveryProfileAPIView.as_view(), name='supplier-profile'),
    path('suppliers/', SuppliersList.as_view(), name='suppliers_list'),
    path('suppliers/<int:pk>/', SupplierDetail.as_view(), name='supplier_detail'),
    path('followsupplier/<int:supplier_id>/', FollowSupplier.as_view(), name='follow_supplier'),
    path('trending-suppliers/', TrendingSuppliersAPIView.as_view(), name='trending_suppliers'),
    path('', include(router.urls)),

]

    
