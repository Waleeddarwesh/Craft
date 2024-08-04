from datetime import timedelta
from django.utils.timezone import now
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Customer, Supplier, Delivery,User,Address
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError 
from .utils import send_normal_email
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from products.models import Product ,Category
from products.serializers import ProductImageSerializer
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','PhoneNO','date_joined']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','BuildingNO','Street','City','State']

class AcountProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id','images','ProductName', 'UnitPrice']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data['images']:
            data['images'] = [data['images'][0]]  # Include only the first image
        return data

class CustomerRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"})
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2','PhoneNO')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"error": "Passwords do not match"})
        if len(attrs['password']) < 8 or not any(char.isdigit() for char in attrs['password']):
            raise serializers.ValidationError({"error": "Password must be at least 8 characters long and contain at least one digit"})
        
        # Check if PhoneNO already exists in the database
        if User.objects.filter(PhoneNO=attrs['PhoneNO']).exists():
            raise serializers.ValidationError({"error": "Phone number already exists"})
        
        return attrs

    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            PhoneNO=self.validated_data['PhoneNO'],
            is_customer=True
        )
        user.password = self.validated_data['password']  # Hash the password
        user.save()
        Customer.objects.create(
            user=user
        )
        return user

class CategoreyTitle(serializers.ModelSerializer):
    class Meta:
       model = Category
       fields =('Title')

class SupplierRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"})
    CategoryTitle = serializers.CharField(required=True)
    ExperienceYears = serializers.IntegerField(required=True)
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2','PhoneNO','CategoryTitle','ExperienceYears')    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"error": "Passwords do not match"})
        if len(attrs['password']) < 8 or not any(char.isdigit() for char in attrs['password']):
            raise serializers.ValidationError({"error": "Password must be at least 8 characters long and contain at least one digit"})
        
        # Check if PhoneNO already exists in the database
        if User.objects.filter(PhoneNO=attrs['PhoneNO']).exists():
            raise serializers.ValidationError({"error": "Phone number already exists"})
        
        return attrs
    
    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            PhoneNO=self.validated_data['PhoneNO'],
            is_supplier=True
        )
        user.password = self.validated_data['password']  # Hash the password
        user.save()
        Supplier.objects.create(
           user=user,
           CategoryTitle=self.validated_data['CategoryTitle'],
            ExperienceYears=self.validated_data['ExperienceYears'],
           )
        return user
 
class DeliveryRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"})
    plateNO = serializers.CharField(required=True)
    VehicleModel = serializers.CharField(required=True)
    governorate = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'password2', 'PhoneNO', 'plateNO','VehicleModel','governorate')
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"error": "Passwords do not match"})
        if len(attrs['password']) < 8 or not any(char.isdigit() for char in attrs['password']):
            raise serializers.ValidationError({"error": "Password must be at least 8 characters long and contain at least one digit"})
        
        # Check if PhoneNO already exists in the database
        if User.objects.filter(PhoneNO=attrs['PhoneNO']).exists():
            raise serializers.ValidationError({"error": "Phone number already exists"})
        
        return attrs
    
    def save(self, **kwargs):
        user = User(
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            is_delivery=True
        )
        user.password = self.validated_data['password']  # Hash the password
        user.save()
        Delivery.objects.create(
            user=user,
            plateNO=self.validated_data['plateNO'],
            VehicleModel=self.validated_data['VehicleModel'],
            governorate=self.validated_data['governorate'],
        )
        return user
    
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=155, min_length=6)
    password=serializers.CharField(max_length=68, write_only=True)
    full_name=serializers.CharField(max_length=255, read_only=True)
    access_token=serializers.CharField(max_length=255, read_only=True)
    refresh_token=serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']


    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request=self.context.get('request')
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("invalid credential try again")
        if not user.is_verified:
            raise AuthenticationFailed("Email is not verified")
        tokens=user.tokens()
        return {
            'email':user.email,
            'full_name':user.get_full_name,
            "access_token":str(tokens.get('access')),
            "refresh_token":str(tokens.get('refresh'))
        }

class CustomerProfileSerializer(serializers.ModelSerializer):
 user = UserSerializer()
 class Meta:
        model = Customer
        fields =  ["id",'user','CustomerPhoto','Balance']

 def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance   
 
class SupplierProfileSerializer(serializers.ModelSerializer):
 user = UserSerializer()
 products = AcountProductSerializer(many=True, source='product_set') 
 class Meta:
        model = Supplier
        fields =  ["id",'user','SupplierCover','SupplierPhoto','CategoryTitle','ExperienceYears','Rating','Orders','Balance','products']

 def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class deliveryProfileSerializer(serializers.ModelSerializer):
 user = UserSerializer()
 class Meta:
        model = Delivery
        fields =  ["id",'user','DeliveryPhoto','Rating','Orders','Balance','ExperienceYears','VehicleModel','plateNO']
 def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class CraftersSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    SupplierProducts = AcountProductSerializer(many=True, read_only=True)
    class Meta:
        model = Supplier
        fields = ('id','user', 'SupplierPhoto', 'SupplierProducts')

    def get_user(self, obj):
        return {'full_name': obj.user.get_full_name}
    
class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

class SetNewPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=4, min_length=4, write_only=True)
    new_password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=8, write_only=True)
    class Meta:
        fields = ['otp', 'new_password', 'confirm_password']
        
class LogoutUserSerializer(serializers.Serializer):
    refresh_token=serializers.CharField()

    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')

        return attrs

    def save(self, **kwargs):
        try:
            token=RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            return self.fail('bad_token')

from .utils import Google, register_social_user
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

class GoogleSignInSerializer(serializers.Serializer):
    access_token=serializers.CharField(min_length=6)
    def validate_access_token(self, access_token):
        user_data=Google.validate(access_token)
        try:
            user_data['sub']
            
        except:
            raise serializers.ValidationError("this token has expired or invalid please try again")
        
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
                raise AuthenticationFailed('Could not verify user.')

        user_id=user_data['sub']
        email=user_data['email']
        first_name=user_data['given_name']
        last_name=user_data['family_name']
        provider='google'

        return register_social_user(provider, email, first_name, last_name)
class SupplierDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['SupplierContract', 'SupplierIdentity']
        
class deliveryDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['DeliveryContract', 'DeliveryIdentity']