import re
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from .permissions import IsCustomerorSupplier
from . import permissions
from .serializers import CustomerRegistrationSerializer,SupplierRegistrationSerializer,DeliveryRegistrationSerializer,AddressSerializer
from .serializers import LoginSerializer,SetNewPasswordSerializer,LogoutUserSerializer
from .serializers import CustomerProfileSerializer,deliveryProfileSerializer,SupplierProfileSerializer,CraftersSerializer,SupplierDocumentSerializer,deliveryDocumentSerializer
from .utils import send_generated_otp_to_email
from rest_framework.generics import GenericAPIView,ListAPIView
from rest_framework.response import Response
from rest_framework import status ,viewsets
from .utils import OneTimePassword
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework.permissions import IsAuthenticated
from .models import User,Supplier,Customer,Delivery,Follow,Address
from products.models import Product,ProImage
from rest_framework.views import APIView 
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import AnonymousUser
from django.http import FileResponse
# the registration based on the customer.
class RegisterViewforcustomer(GenericAPIView):
    serializer_class = CustomerRegistrationSerializer
    def post(self, request):
        user = request.data
        PhoneNO = user.get('PhoneNO', None)
        if not re.match(r'^(010|011|012|015)\d{8}$', str(PhoneNO)):
            return Response({'error': 'the phone number you entered is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            send_generated_otp_to_email(user_data['email'], request)
            return Response({
                'data':user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterViewforSupplier(GenericAPIView):
    serializer_class = SupplierRegistrationSerializer
    def post(self, request):
        user = request.data
        PhoneNO = user.get('PhoneNO', None)
        if not re.match(r'^(010|011|012|015)\d{8}$', PhoneNO):
            return Response({'error': 'the phone number you entered is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            send_generated_otp_to_email(user_data['email'], request)
            return Response({
                'data':user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterViewforDelivery(GenericAPIView):
    serializer_class =DeliveryRegistrationSerializer
    def post(self, request):
        user = request.data
        phone_number = user.get('PhoneNO', None)
        if not re.match(r'^(010|011|012|015)\d{8}$', phone_number):
            return Response({'error': 'the phone number you entered is invalid'}, status=status.HTTP_400_BAD_REQUEST)
        serializer=self.serializer_class(data=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user_data=serializer.data
            send_generated_otp_to_email(user_data['email'], request)
            return Response({
                'data':user_data,
                'message':'thanks for signing up a passcode has be sent to verify your email'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        try:
            passcode = request.data.get('otp')
            user_pass_obj=OneTimePassword.objects.get(otp=passcode)
            user=user_pass_obj.user
            if not user.is_verified:
                user.is_verified=True
                user.save()
                return Response({
                    'message':'account email verified successfully'
                }, status=status.HTTP_200_OK)
            return Response({'message':'passcode is invalid user is already verified'}, status=status.HTTP_204_NO_CONTENT)
        except OneTimePassword.DoesNotExist as identifier:
            return Response({'message':'passcode not provided'}, status=status.HTTP_400_BAD_REQUEST)

class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    def post(self, request):
        serializer= self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CustomerProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, user):
        try:
            return Customer.objects.get(user=user)
        except Customer.DoesNotExist:
            raise Http404("Customer does not exist ")
        
    def get(self, request, format=None):
        customer = self.get_object(request.user)
        serializer = CustomerProfileSerializer(customer)
        return Response(serializer.data)
    
    def put(self, request, format=None):
        customer = self.get_object(request.user)
        serializer = CustomerProfileSerializer(customer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SupplierProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, user):
        try:
            return Supplier.objects.get(user=user)
        except Supplier.DoesNotExist:
            raise Http404("SupplierProfile does not exist ")
    def get(self, request, format=None):
        supplier = self.get_object(request.user)
        serializer = SupplierProfileSerializer(supplier)
        return Response(serializer.data)

    def put(self, request, format=None):
        supplier = self.get_object(request.user)
        serializer = SupplierProfileSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeliveryProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, user):
        try:
            return Delivery.objects.get(user=user)
        except Delivery.DoesNotExist:
            raise Http404("Delivery Profile does not exist ")
                   
    def get(self, request, format=None):
        delivery = self.get_object(request.user)
        serializer = deliveryProfileSerializer(delivery)
        return Response(serializer.data)
        
    def put(self, request, format=None):
        delivery = self.get_object(request.user)
        serializer = deliveryProfileSerializer(delivery, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SuppliersList(ListAPIView):
    queryset = Supplier.objects.filter(user__is_verified=True,user__is_active=True).order_by('id')
    serializer_class = CraftersSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['CategoryTitle','Rating','ExperienceYears']
    search_fields = ['user_first_name', 'user_last_name']
    ordering_fields = ['user_first_name']
    pagination_class = StandardResultsSetPagination
# filters, search terms, or ordering
    def get_serializer_context(self):
        return {'request': self.request}

    def get(self, request, *args, **kwargs):
     response = super().get(request, *args, **kwargs)
    
    # Transform the data to include only the desired fields
     transformed_data = []
     for supplier in response.data.get('results', []):
        if isinstance(supplier, dict):  # Check if supplier is a dictionary
            transformed_supplier = {
                "id": supplier.get('id', ''),  # Use .get() method to safely access 'id'
                'full_name': supplier['user']['full_name'] if 'user' in supplier else '',
                'SupplierPhoto': supplier.get('SupplierPhoto', ''),
            }
            transformed_data.append(transformed_supplier)
        else:
            print(f"Invalid supplier data: {supplier}")

     return Response(transformed_data)

class TrendingSuppliersAPIView(APIView):
    permission_classes = [IsCustomerorSupplier] 
    def get(self, request, format=None):
        trending_suppliers = Supplier.objects.order_by('-Rating','-Orders')[:10]  # Fetch top 10 suppliers based on rating
        serializer = CraftersSerializer(trending_suppliers, many=True)
        return Response(serializer.data)
    
class SupplierDetail(APIView):
    def get(self, request, pk):
        supplier = get_object_or_404(Supplier, pk=pk)
        serializer_context = {
            'request': request,
        }
        serializer = CraftersSerializer(supplier, context=serializer_context)
        # Transform the data to include only the desired fields for the supplier
        transformed_supplier = {
            "id": supplier.user.id,
            'full_name': supplier.user.get_full_name,
            'SupplierPhoto': supplier.SupplierPhoto.url if supplier.SupplierPhoto else None,
            'SupplierCover': supplier.SupplierCover.url if supplier.SupplierCover else None,
            'CategoryTitle': supplier.CategoryTitle,
            'ExperienceYears': supplier.ExperienceYears,
            'Orders': supplier.Orders,
            'Rating': supplier.Rating,
            'SupplierProducts': [
                {
                    'id': product.id,
                    'photo': product.images.first().image.url if product.images.first() else None,
                    'ProductName': product.ProductName,
                    'UnitPrice':product.UnitPrice,
                } for product in supplier.product_set.all()
            ]
        }
        return Response(transformed_supplier, status=status.HTTP_200_OK)

class FollowSupplier(APIView):
    def post(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            user = request.user
            customer = user.customer  # Assuming user is a customer
            follow_exists = Follow.objects.filter(Customer=customer, Supplier=supplier).exists()
            if follow_exists:
                return Response({'message': 'You have already followed this supplier'}, status=status.HTTP_400_BAD_REQUEST)
            else:
             Follow.objects.create(Customer=customer, Supplier=supplier)
             supplier.save()
            return Response({'message': 'Followed'}, status=status.HTTP_201_CREATED)
        except Customer.DoesNotExist:
            return Response({'message': 'User is not a customer'}, status=status.HTTP_400_BAD_REQUEST)
        except Supplier.DoesNotExist:
            return Response({'message': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, supplier_id):
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            user = request.user
            customer = user.customer  # Assuming user is a customer
            follow = Follow.objects.get(Customer=customer, Supplier=supplier)
            follow.delete()
            supplier.FollowersNo -= 1
            supplier.save()
            return Response({'message': 'Unfollowed'}, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({'message': 'User is not a customer'}, status=status.HTTP_400_BAD_REQUEST)
        except Supplier.DoesNotExist:
            return Response({'message': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)
        except Follow.DoesNotExist:
            return Response({'message': 'You are not following this supplier'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
          

from django.utils.timezone import now, timedelta
from .serializers import EmailVerificationSerializer
from django.core.mail import EmailMessage
import random
from django.conf import settings
from .models import User, OneTimePassword

class PasswordResetRequestView(APIView):
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            # Check if a recent password reset request exists
            if user.last_password_reset_request is not None and now() - user.last_password_reset_request < timedelta(minutes=1):
                return Response({"error": "Please wait 1 minute before attempting another password reset."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Generate OTP and send email
            otp = random.randint(1000, 9999)
            OneTimePassword.objects.update_or_create(user=user, defaults={'otp': otp})

            # Sending email
            subject = "One time passcode for Password Reset"
            email_body = f"Hi {user.first_name}, use this OTP to reset your password: {otp}"
            from_email = settings.EMAIL_HOST_USER
            to_email = [user.email]
            email = EmailMessage(subject, email_body, from_email, to_email)
            email.send()

            # Update last password reset request time
            user.last_password_reset_request = now()
            user.save()

            return Response({"message": "OTP sent to your email for password reset."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "User with that email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
class SetNewPasswordView(APIView):
    serializer_class = SetNewPasswordSerializer
    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        confirm_password = serializer.validated_data['confirm_password']

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        otp_record = OneTimePassword.objects.filter(otp=otp).first()

        if not otp_record or otp_record.user.last_login > otp_record.created_at:
            return Response({"error": "Invalid OTP or OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        user = otp_record.user
        user.set_password(new_password)
        user.save()

        otp_record.delete()  # Delete OTP record after successful password reset

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
    
class LogoutApiView(GenericAPIView):
    serializer_class=LogoutUserSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

from .serializers import GoogleSignInSerializer
class GoogleOauthSignInview(GenericAPIView):
    serializer_class=GoogleSignInSerializer

    def post(self, request):
        print(request.data)
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=((serializer.validated_data)['access_token'])
        return Response(data, status=status.HTTP_200_OK) 

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Address.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
class SupplierDocumentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Provide the contract for download
        file_path = 'contract/contract_temp.pdf'
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='contract_template.pdf')

    def create(self, request):
        try:
            supplier = request.user.supplier
        except Supplier.DoesNotExist:
            return Response({'error': 'Supplier profile does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SupplierDocumentSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class deliveryDocumentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Provide the contract for download
        file_path = 'contract/contract_temp.pdf'
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='contract_template.pdf')

    def create(self, request):
        try:
            delivery = request.user.delivery
        except Delivery.DoesNotExist:
            return Response({'error': 'delivery profile does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = deliveryDocumentSerializer(delivery, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)