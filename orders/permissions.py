from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission
from products.models import Product
from orders.models import Order,Cart
from rest_framework import permissions
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.exceptions import ValidationError

class IsOrderPending(BasePermission):
    """
    Check the status of order is pending or completed before updating/deleting instance
    """
    message = _("Updating or deleting closed order is not allowed.")

    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve",):
            return True
        return obj.status == "P"

class IsOrderItemByBuyerOrAdminordelivery(BasePermission):
    """
    Check if order item is owned by appropriate buyer or admin
    """

    def has_permission(self, request, view):
        order_id = view.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id)
        return order.user == request.user or request.user.is_staff or request.user.is_delivery
    def has_object_permission(self, request, view, obj):
        return obj.order.user == request.user or request.user.is_staff or request.user.is_delivery

class CanOrderFromOtherSuppliers(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method == 'POST' and view.action == 'create':
            items = request.data.get('items', [])
            for item in items:
                product_id = item.get('product', {}).get('id')
                product_supplier_id = Product.objects.filter(id=product_id).values_list('Supplier_id', flat=True).first()
                if product_supplier_id == request.user.id:
                    return False
        
        return True

class IsOrderItemPending(BasePermission):
    """
    Check the status of order is pending or completed before creating, updating and deleting order items
    """

    message = _(
        "Creating, updating or deleting order items for a closed order is not allowed."
    )

    def has_permission(self, request, view):
        order_id = view.kwargs.get("order_id")
        order = get_object_or_404(Order, id=order_id)

        if view.action in ("list",):
            return True

        return order.status == "P"

    def has_object_permission(self, request, view, obj):
        if view.action in ("retrieve",):
            return True
        return obj.order.status == "P"
    
class IsSupplier(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'supplier')
    
class DeliveryContractProvided(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and hasattr(user, 'delivery'):
            delivery = user.delivery
            if not delivery.DeliveryContract and not delivery.DeliveryIdentity:
             channel_layer = get_channel_layer()
             async_to_sync(channel_layer.group_send)(
              f"user_{request.user.id}",
              {
              "type": "send_notification",
             "message": "upload your contract please ."
               }
               )
             return False
         # Check if the supplier is marked as accepted
            if not delivery.accepted_delivery:
                raise ValidationError("Your delivery account has not been accepted yet.the adminstrators will accept your documents soon ")
            
        return True