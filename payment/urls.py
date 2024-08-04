from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet,payment_completed,payment_canceled,CoursePaymentViewSet
from . import webhook

app_name = "payment"

router = DefaultRouter()
router.register('payment',PaymentViewSet, basename="payment")
router.register('course-payment', CoursePaymentViewSet, basename='course-payment')

urlpatterns = [
    path('success/',payment_completed , name='success'),
    path('canceled/', payment_canceled, name='cancel'),
    path('webhook/', webhook.stripe_webhook, name='stripe-webhook'),
    path('', include(router.urls)),
]