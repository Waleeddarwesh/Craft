from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated 

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user,'customer')
                                                            
class IsSupplier(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'supplier' attribute
        return request.user.is_authenticated and hasattr(request.user, 'supplier')

class IsCustomerorSupplier(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'supplier' attribute
        return request.user.is_authenticated and hasattr(request.user, 'supplier') or hasattr(request.user, 'customer')
