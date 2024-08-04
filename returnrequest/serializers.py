from rest_framework import serializers
from products.models import Product
from .models import ReturnRequest,Balance_Withdraw_Request,transactions,DeliveryReturnRequest
from orders.serializers import UserSerializer,AddressSerializer,SimpleProductSerializer

class ReturnRequestCreateSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()

    def validate_product_id(self, value):
        product = Product.objects.filter(id=value).first()
        if not product:
            raise serializers.ValidationError("There is no product associated with the given ID")
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]
        product = Product.objects.get(id=product_id)
        
        if product.Supplier.user == user:
            raise serializers.ValidationError("You cannot return your own product to the cart")
        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be above 0")
        
        return self.instance

    class Meta:
        model = ReturnRequest
        fields = ['product_id', 'quantity']

class ReturnRequestListRetrieveSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    address = AddressSerializer(many=False,read_only=True)
    from_address =AddressSerializer(many=False,read_only=True)
    confirmation_code = serializers.SerializerMethodField()
    product = SimpleProductSerializer(many=False, allow_null=True)
    
    class Meta:
        model = ReturnRequest
        fields = ("id","user","address","from_address","product","amount","status", "created_at",'confirmation_code')

    def get_confirmation_code(self, obj: ReturnRequest):
        request = self.context.get('request')
        if request and request.user == obj.user:
            return obj.confirmation_code
        return None  

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['confirmation_code'] is None:
            data.pop('confirmation_code')  
        return data

class DeliveryReturnRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryReturnRequest
        fields = ['confirmation_code']
        extra_kwargs = {'confirmation_code': {'write_only': True}}

class OrderItemListRetrieveSerializer(serializers.ModelSerializer):
    cost = serializers.SerializerMethodField()
    product = SimpleProductSerializer()

    class Meta:
        model = ReturnRequest
        fields = ("id", "product", "quantity", "price", "cost")

    def get_cost(self, obj: ReturnRequest):
        return obj.get_cost()
        
class BalanceWithdrawRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance_Withdraw_Request
        fields = '__all__'
   
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = transactions
        fields = '__all__'