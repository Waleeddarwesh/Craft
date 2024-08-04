from django.urls import path,include
from .views import (
    ReturnRequestViewSet,
    BalanceWithdrawRequestListCreateView,
    BalanceWithdrawRequestDetailView,
    get_user_transactions
)
from rest_framework.routers import DefaultRouter
from orders.models import Order

router = DefaultRouter()
router.register('return-requests', ReturnRequestViewSet, basename='return-request')

urlpatterns = [
    path('', include(router.urls)),
    path('withdraw-requests/', BalanceWithdrawRequestListCreateView.as_view(), name='balance-withdraw-request-list-create'),
    path('withdraw-requests/<int:pk>/', BalanceWithdrawRequestDetailView.as_view(), name='balance-withdraw-request-detail'),
    path('transactions/', get_user_transactions, name='get-user-transactions'),
]
