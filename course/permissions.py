from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'customer')
                                                            
class IsSupplier(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'supplier' attribute
        return request.user.is_authenticated and hasattr(request.user, 'supplier')

    def has_object_permission(self, request, view, obj):
        # Check if the user is the supplier of the specific course (obj)
        return hasattr(obj, 'Supplier') and obj.Supplier == request.user.supplier

class IsSupplierOrCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (hasattr(request.user, 'supplier') or hasattr(request.user, 'customer'))
