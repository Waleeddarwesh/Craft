from .models import Order,OrderItem,Cart,CartItems,Wishlist,WishlistItem,Warehouse
from accounts.serializers import AddressSerializer
from products .models import Product
from .models import Coupon
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from products.serializers import ProductImageSerializer

class SimpleProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ["id",'images',"ProductName", "UnitPrice"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['images']:
            data['images'] = [data['images'][0]]  # Include only the first image
        return data
    
class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "name", "PhoneNO"]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class WishlistItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(many=False, allow_null=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product"]

class WishlistSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = WishlistItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ["id", "items"]

class AddWishlistItemSerializer(serializers.ModelSerializer):
    Product_id = serializers.IntegerField()

    def validate_Product_id(self, value):
        product = Product.objects.filter(id=value).first()
        if not product:
            raise serializers.ValidationError("There is no product associated with the given ID")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        Product_id = self.validated_data["Product_id"]
        wishlist, _ = Wishlist.objects.get_or_create(user=user)

        # Check if the product is owned by the user
        product = Product.objects.get(id=Product_id)
        if product.supplier.user == user:
            raise serializers.ValidationError("You cannot add your own product to the wishlist")

        wishlist_item, _ = WishlistItem.objects.get_or_create(wishlist=wishlist, Product_id=Product_id)
        self.instance = wishlist_item

        return self.instance

    class Meta:
        model = WishlistItem
        fields = ["id", "Product_id"]
        
class AddWishlistItemSerializer(serializers.ModelSerializer):
    Product_id = serializers.IntegerField()

    def validate_Product_id(self, value):
        product = Product.objects.filter(id=value).first()
        if not product:
            raise serializers.ValidationError("There is no product associated with the given ID")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        Product_id = self.validated_data["Product_id"]
        wishlist, _ = Wishlist.objects.get_or_create(user=user)

        # Check if the product is owned by the user
        product = Product.objects.get(id=Product_id)
        if product.supplier.user == user:
            raise serializers.ValidationError("You cannot add your own product to the wishlist")

        wishlist_item, _ = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)  # Corrected field name
        self.instance = wishlist_item

        return self.instance

    class Meta:
        model = WishlistItem
        fields = ["id", "Product_id"]

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(many=False, allow_null=True)
    sub_total = serializers.SerializerMethodField(method_name="total")

    class Meta:
        model = CartItems
        fields = ["id", "Quantity", "product", "sub_total"]

    def total(self, cart_item):
        if cart_item.Product:
            return cart_item.Quantity * cart_item.Product.UnitPrice
        return 0

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField(method_name='main_total')
    
    class Meta:
        model = Cart
        fields = ["id", "items", "grand_total"]
        
    def main_total(self, cart):
        items = cart.items.all()
        total = sum([item.Quantity * item.product.UnitPrice for item in items if item.product])
        return total
       
class AddCartItemSerializer(serializers.ModelSerializer):
    Product_id = serializers.IntegerField()

    def validate_Product_id(self, value):
        product = Product.objects.filter(id=value).first()
        if not product:
            raise serializers.ValidationError("There is no product associated with the given ID")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        Product_id = self.validated_data["Product_id"]
        quantity = self.validated_data["Quantity"]
        cart, _ = Cart.objects.get_or_create(User=user)

        # Check if the product is owned by the user
        product = Product.objects.get(id=Product_id)
        if product.Supplier.user == user:
            raise serializers.ValidationError("You cannot add your own product to the cart")
        
        if quantity == 0 :
            raise serializers.ValidationError(" Quantity Must be above 0 ")
        try:
            cart_item = CartItems.objects.get(Product_id=Product_id, CartID=cart)
            cart_item.Quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItems.DoesNotExist:
            self.instance = CartItems.objects.create(CartID=cart, Product_id=Product_id, Quantity=quantity)

        return self.instance

    class Meta:
        model = CartItems
        fields = ["id", "Product_id", "Quantity"]

class UpdateCartItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    class Meta:
        model = CartItems
        fields = ["Quantity"]

class OrderCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Order
        exclude = ("cart", "paid", "status", "stripe_id")
        
class OrderItemListRetrieveSerializer(serializers.ModelSerializer):
    cost = serializers.SerializerMethodField()
    order = serializers.StringRelatedField()
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ("id", "order", "product", "quantity", "price", "cost")

    def get_cost(self, obj: OrderItem):
        return obj.get_cost()

class OrderListRetrieveSerializer(serializers.ModelSerializer):
    items = OrderItemListRetrieveSerializer(many=True, read_only=True)
    total_cost = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    address = AddressSerializer(many=False,read_only=True)
    from_address =AddressSerializer(many=False,read_only=True)
    confirmation_code = serializers.SerializerMethodField()
    payment_method = serializers.ChoiceField(choices=Order.PaymentMethod.choices)
    
    class Meta:
        model = Order
        fields = ("id","user","address","from_address","items", "total_cost","payment_method" ,"status", "created_at", "updated_at",'confirmation_code')

    def get_total_cost(self, obj: Order):
        return obj.get_total_cost()
    
    def get_confirmation_code(self, obj: Order):
        # Check if the requester is the creator of the order
        request = self.context.get('request')
        if request and request.user == obj.user:
            return obj.confirmation_code
        return None  # If requester is not the creator, return None or exclude the field

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['confirmation_code'] is None:
            data.pop('confirmation_code')  # Remove confirmation_code if it's None
        return data

class ReturnRequestListRetrieveSerializer(serializers.ModelSerializer):
    items = OrderItemListRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["items",]
        ref_name = 'Orders_ReturnRequestListRetrieveSerializer'

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount', 'valid_from', 'valid_to']
    
    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated or not hasattr(user, 'supplier'):
            raise serializers.ValidationError("User is not a supplier.")
        
        validated_data['supplier'] = user.supplier
        return super().create(validated_data)
    
class OrderDeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['confirmation_code']
        extra_kwargs = {'confirmation_code': {'write_only': True}}

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id','name',]