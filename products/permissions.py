from rest_framework import permissions
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.exceptions import ValidationError

class IsSupplier(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'supplier')

class SupplierContractProvided(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated and hasattr(user, 'supplier'):
            supplier = user.supplier
            if not supplier.SupplierContract and not supplier.SupplierIdentity:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{request.user.id}",
                    {
                        "type": "send_notification",
                        "message": "Upload your contract and identity documents, please."
                    }
                )
                return False
            
            # Check if the supplier is marked as accepted
            if not supplier.accepted_supplier:
                raise ValidationError("Your supplier account has not been accepted yet.the adminstrators will accept your documents soon ")
            
        return True
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
