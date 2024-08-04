from rest_framework import generics, status
from rest_framework.response import Response
from products.models import Product
from .models import Review
from rest_framework.exceptions import NotFound
from .serializers import *
from accounts.permissions import *

class ProductReviewCreate(generics.CreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class ProductReviewUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.filter(product__isnull=False)
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return super().get_object()
        except Review.DoesNotExist:
            raise NotFound({"detail": "Review not found."})
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        customer_instance = instance.customer
        if customer_instance.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        customer_instance = instance.customer
        if customer_instance.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class ProductReviewList(generics.ListAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get('product_id')
        queryset = Review.objects.filter(product_id=product_id)
        if not queryset.exists():
            raise NotFound({"detail": "No reviews found for this product."})
        return queryset
    
class CourseReviewCreate(generics.CreateAPIView):
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class CourseReviewUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.filter(course__isnull=False)
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return super().get_object()
        except Review.DoesNotExist:
            raise NotFound({"detail": "Review not found."})
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        customer_instance = instance.customer
        if customer_instance.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        customer_instance = instance.customer
        if customer_instance.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

class CourseReviewList(generics.ListAPIView):
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        if not Review.objects.filter(id=course_id).exists():
            raise NotFound({"detail": "Course not found."})
        queryset = Review.objects.filter(course_id=course_id)
        if not queryset.exists():
            raise NotFound({"detail": "No reviews found for this Course."})
        return queryset
    
class DeliveryReviewCreate(generics.CreateAPIView):
    serializer_class = DeliveryReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class DeliveryReviewUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.filter(delivery__isnull=False)
    serializer_class = DeliveryReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return super().get_object()
        except Review.DoesNotExist:
            raise NotFound({"detail": "Review not found."})
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        customer_instance = instance.customer
        if customer_instance.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        customer_instance = instance.customer
        if customer_instance.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
    
class DeliveryReviewList(generics.ListAPIView):
    serializer_class = DeliveryReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        delivery_id = self.kwargs.get('delivery_id')
        if not Delivery.objects.filter(id=delivery_id).exists(): 
            raise NotFound({"detail": "Delivery not found."})
        queryset = Review.objects.filter(delivery_id=delivery_id)
        if not queryset.exists():
            raise NotFound({"detail": "No reviews found for this delivery."})
        return queryset

class SupplierReviewCreate(generics.CreateAPIView):
    serializer_class = SupplierReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        customer_instance = self.request.user.customer  # Assuming there is a one-to-one relationship between User and Customer
        serializer.save(customer=customer_instance)

class SupplierReviewUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.filter(supplier__isnull=False)
    serializer_class = SupplierReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return super().get_object()
        except Review.DoesNotExist:
            raise NotFound({"detail": "Review not found."})
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.customer.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.customer.user != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
        
class SupplierReviewList(generics.ListAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        supplier_id = self.kwargs.get('supplier_id')
        if not Supplier.objects.filter(id=supplier_id).exists(): 
            raise NotFound({"detail": "Supplier not found."})
        products = Product.objects.filter(supplier_id=supplier_id)
        if not products.exists():
            raise NotFound({"detail": "No products found for this supplier."})
        queryset = Review.objects.filter(product__in=products)
        if not queryset.exists():
            raise NotFound({"detail": "No reviews found for this supplier's products."})
        return queryset

