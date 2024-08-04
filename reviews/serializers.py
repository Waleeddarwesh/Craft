from rest_framework import serializers
from .models import Review
from accounts.models import Customer,Delivery,Supplier
from products.models import Product
from course.models import Course

class ProductReviewSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Review
        fields = ['id', 'customer', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at',]

    def create(self, validated_data):
        try:
            customer_instance = Customer.objects.get(user=self.context['request'].user)
        except Customer.DoesNotExist:
            # If there is no corresponding Customer instance, raise a ValidationError
            raise serializers.ValidationError("You must be a customer to make a review.")

        # Extract the product ID from the request data
        product_id = self.context['request'].data.get('product_id')

        # Check if the product exists
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product ID.")

        if Review.objects.filter(customer=customer_instance, product=product).exists():
            # If a review already exists for the customer and product, raise a ValidationError
            raise serializers.ValidationError("You have already reviewed this product.")

        # Remove the 'customer' key from validated_data
        validated_data.pop('customer', None)

        return Review.objects.create(customer=customer_instance, product=product, **validated_data)

    def update(self, instance, validated_data):
        instance.rating = validated_data.get('rating', instance.rating)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance

class CourseReviewSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Review
        fields = ['id', 'customer', 'course', 'rating', 'comment','image', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        try:
            customer_instance = Customer.objects.get(user=self.context['request'].user)
        except Customer.DoesNotExist:
            # If there is no corresponding Customer instance, raise a ValidationError
            raise serializers.ValidationError("You must be a customer to make a review.")

        # Extract the course ID from the request data
        course_id = self.context['request'].data.get('course_id')

        # Check if the course exists
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Invalid course ID.")

        if Review.objects.filter(customer=customer_instance, course=course).exists():
            # If a review already exists for the customer and course, raise a ValidationError
            raise serializers.ValidationError("You have already reviewed this course.")

        # Remove the 'customer' key from validated_data
        validated_data.pop('customer', None)

        return Review.objects.create(customer=customer_instance, course=course, **validated_data)

    def update(self, instance, validated_data):
        instance.rating = validated_data.get('rating', instance.rating)
        instance.image = validated_data.get('image', instance.image)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

class DeliveryReviewSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Review
        fields = ['id', 'customer', 'delivery', 'rating', 'ease_of_place_order','speed_of_delivery','product_packaging', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        try:
            customer_instance = Customer.objects.get(user=self.context['request'].user)
        except Customer.DoesNotExist:
            # If there is no corresponding Customer instance, raise a ValidationError
            raise serializers.ValidationError("You must be a customer to make a review.")

        # Extract the delivery ID from the request data
        delivery_id = self.context['request'].data.get('delivery_id')

        # Check if the delivery exists
        try:
            delivery = Delivery.objects.get(pk=delivery_id)
        except Delivery.DoesNotExist:
            raise serializers.ValidationError("Invalid delivery ID.")

        if Review.objects.filter(customer=customer_instance, delivery=delivery).exists():
            # If a review already exists for the customer and delivery, raise a ValidationError
            raise serializers.ValidationError("You have already reviewed this delivery.")

        # Remove the 'customer' key from validated_data
        validated_data.pop('customer', None)

        return Review.objects.create(customer=customer_instance, delivery=delivery, **validated_data)

    def update(self, instance, validated_data):
        instance.rating = validated_data.get('rating', instance.rating)
        instance.ease_of_place_order = validated_data.get('ease_of_place_order', instance.ease_of_place_order)
        instance.speed_of_delivery = validated_data.get('speed_of_delivery', instance.speed_of_delivery)
        instance.product_packaging = validated_data.get('product_packaging', instance.product_packaging)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance

class SupplierReviewSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ['id', 'customer', 'supplier', 'rating', 'comment','image', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        try:
            customer_instance = Customer.objects.get(user=self.context['request'].user)
        except Customer.DoesNotExist:
            # If there is no corresponding Customer instance, raise a ValidationError
            raise serializers.ValidationError("You must be a customer to make a review.")

        # Extract the supplier ID from the request data
        supplier_id = self.context['request'].data.get('supplier_id')

        # Check if the supplier exists
        try:
            supplier = Supplier.objects.get(pk=supplier_id)
        except Supplier.DoesNotExist:
            raise serializers.ValidationError("Invalid supplier ID.")

        if Review.objects.filter(customer=customer_instance, supplier=supplier).exists():
            # If a review already exists for the customer and supplier, raise a ValidationError
            raise serializers.ValidationError("You have already reviewed this supplier.")

        # Remove the 'customer' key from validated_data
        validated_data.pop('customer', None)

        return Review.objects.create(customer=customer_instance, supplier=supplier, **validated_data)

    def update(self, instance, validated_data):
        instance.rating = validated_data.get('rating', instance.rating)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance
