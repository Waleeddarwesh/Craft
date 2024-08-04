from rest_framework import generics, serializers
from .models import Balance_Withdraw_Request,transactions,ReturnRequest,DeliveryReturnRequest,User
from accounts.models import Address,Supplier,Delivery
from products.models import Product
from orders.models import Warehouse,DeliveryOrder,Order,OrderItem
from orders.serializers import OrderDeliverSerializer
from .serializers import (BalanceWithdrawRequestSerializer,TransactionSerializer,
                          ReturnRequestListRetrieveSerializer,ReturnRequestCreateSerializer,)
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework.decorators import action
from django.utils import timezone
from django.db import transaction

Craft = User.objects.get(email = "CraftEG@Craft.com")      
class ReturnRequestViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ReturnRequestCreateSerializer
    queryset = ReturnRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_delivery:
                try:
                    return ReturnRequest.objects.filter(
                        Q(from_state=user.delivery.governorate) & 
                        (Q(delivery_orders__delivery_person=user) | Q(delivery_orders__isnull=True)) &
                        ~Q(status__in=[
                            ReturnRequest.OrderStatus.DELIVERED_SUCCESSFULLY, 
                            ReturnRequest.OrderStatus.ON_MY_WAY, 
                            ReturnRequest.OrderStatus.DELIVERED_TO_First_WAREHOUSE,
                            ReturnRequest.OrderStatus.CANCELLED
                        ])
                    )
                except ObjectDoesNotExist:
                    return ReturnRequest.objects.none() 
            else:
                return ReturnRequest.objects.filter(user=user).exclude(initial_status=ReturnRequest.OrderStatus.In_Transmit)
        return ReturnRequest.objects.none()
    
    def create(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity")
        order_id = request.data.get("order_id")

        if not product_id:
            return Response({"detail": "Please Select Product"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        existing_return_request = ReturnRequest.objects.filter(user=request.user,product=product,order=order).exists()
        if existing_return_request:
            return Response({"detail": "You have already returned this product."}, status=status.HTTP_400_BAD_REQUEST)
        
        order_item = OrderItem.objects.get(order=order)
        if int(quantity)>int(order_item.quantity):
            return Response({"detail": " Quantity exceed Your Quantity."}, status=status.HTTP_400_BAD_REQUEST)    

        address = Address.objects.filter(id=order.address.id).first()
        if not address:
            return Response({"detail": " Address not found."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            Supplier_id = product.Supplier.user
            supplier = Supplier.objects.get(user=Supplier_id)
            SupplierAddress = Address.objects.filter(user=supplier.user).first()
            To_State = SupplierAddress.State
            From_State = address.State    
            
            if From_State == To_State:
                warehouse = Warehouse.objects.get(name=From_State)
                Return_Request = ReturnRequest.objects.create(
                    user=request.user,
                    supplier=supplier,
                    product=product,
                    order=order,
                    quantity=quantity,
                    amount=float(product.UnitPrice) *float(quantity) ,
                    from_address=address,
                    to_address=SupplierAddress,
                    from_state=address.State,
                    to_state=SupplierAddress.State,
                    status=ReturnRequest.OrderStatus.CREATED,
                    initial_status=ReturnRequest.OrderStatus.CREATED,
                )
            else:
                warehouse = Warehouse.objects.get(name=From_State)
                Return_Request = ReturnRequest.objects.create(
                    user=request.user,
                    supplier=supplier,
                    product=product,
                    order=order,
                    quantity=quantity,
                    amount=float(product.UnitPrice) *float(quantity),
                    from_address=address,
                    to_address=warehouse.Address,
                    from_state=address.State,
                    to_state=warehouse.Address.State,
                    status=ReturnRequest.OrderStatus.CREATED,
                    initial_status=ReturnRequest.OrderStatus.CREATED,
                )
                related_order = Return_Request
                warehouse = Warehouse.objects.get(name=SupplierAddress.State)
                Return_Request = ReturnRequest.objects.create(
                    user=request.user,
                    supplier=supplier,
                    product=product,
                    order=order,
                    quantity=quantity,
                    amount=float(product.UnitPrice) *float(quantity),
                    from_address=warehouse.Address,
                    to_address=SupplierAddress,
                    from_state=warehouse.Address.State,
                    to_state=SupplierAddress.State,
                    status=ReturnRequest.OrderStatus.In_Transmit,
                    initial_status=ReturnRequest.OrderStatus.In_Transmit,
                    related_order=related_order
                )

        return Response({
            "message": "Return_Request Created Successfully, Our shipping driver will contact you",
            "Return_Request_id": Return_Request.id,
            "Total amount": Return_Request.amount,
        }, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return ReturnRequestListRetrieveSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['post'], url_path='delivery-accept')
    def delivery_accept(self, request, pk=None):
        Return_Request = self.get_object()
        user = request.user
        
        # Check if the user is a delivery person
        if not user.is_delivery:
            return Response({'detail': 'You are not authorized to accept orders.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the order is already accepted by another delivery person
        if hasattr(Return_Request, 'delivery_order') and DeliveryReturnRequest.delivery_order.delivery_person != user:
            return Response({'detail': 'This order has already been accepted by another delivery person.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update the DeliveryOrder entry
        delivery_order, created = DeliveryReturnRequest.objects.get_or_create(ReturnRequest=Return_Request, defaults={'delivery_person': user})
        if not created and delivery_order.delivery_person != user:
            return Response({'detail': 'This order has already been accepted by another delivery person.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the order status
        Return_Request.status = ReturnRequest.OrderStatus.ON_MY_WAY
        Return_Request.delivery = user.delivery
        Return_Request.save()
        
        return Response({'status': 'Order accepted and status updated to on my way'})
    
    @action(detail=True, methods=['post'], url_path='return-request-delivered')
    def delivery_mark_delivered(self, request, pk=None):
        try:
            user = request.user
            Return_Request = ReturnRequest.objects.get(pk=pk, delivery=user.delivery)
            
            if not user.is_delivery:
                return Response({"detail": "Only delivery persons can mark orders as delivered."}, status=status.HTTP_403_FORBIDDEN)
            
            try:
                delivery_order = DeliveryReturnRequest.objects.get(order=Return_Request, delivery_person=user)
            except delivery_order.DoesNotExist:
                return Response({"detail": "This order is not accepted by you."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = OrderDeliverSerializer(data=request.data)
            
            if serializer.is_valid():
                confirmation_code = serializer.validated_data.get('confirmation_code')
                if confirmation_code != ReturnRequest.confirmation_code:
                    return Response({"detail": "Invalid confirmation code."}, status=status.HTTP_400_BAD_REQUEST)
                
                if ReturnRequest.related_order:
                    Return_Request.status = Order.OrderStatus.DELIVERED_SUCCESSFULLY
                    Return_Request.delivery_confirmed_at = timezone.now()
                    Return_Request.save()
                else:
                    Return_Request.status = Order.OrderStatus.DELIVERED_TO_First_WAREHOUSE
                    Return_Request.delivery_confirmed_at = timezone.now()
                    Return_Request.save()
                with transaction.atomic():
                    warehouse = Warehouse.objects.get(name = user.delivery.governorate )
                    user.Balance += warehouse.delivery_fee-15/100*warehouse.delivery_fee
                    Craft.Balance -= warehouse.delivery_fee-15/100*warehouse.delivery_fee
                    transactions.objects.create(user=user,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                , amount=(warehouse.delivery_fee-15/100*warehouse.delivery_fee))
                    transactions.objects.create(user=Craft.supplier.user,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                , amount= (warehouse.delivery_fee-15/100*warehouse.delivery_fee))
                return Response({'status': 'Order status updated to delivered successfully'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ReturnRequest.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='delivery-accepted-return-request')
    def delivery_accepted_orders(self, request):
        try:
            # Ensure the user is a delivery person and access the related Delivery profile
            delivery_person = request.user
            delivery_profile = delivery_person.delivery
            # Filter orders accepted by the current delivery person
            Return_Request = ReturnRequest.objects.filter(
                delivery_orders__delivery_person=delivery_person,
                delivery_orders__accepted_at__isnull=False,
                status=ReturnRequest.OrderStatus.ON_MY_WAY
            )
            serializer = self.get_serializer(Return_Request, many=True)
            return Response(serializer.data)
        except Delivery.DoesNotExist:
            return Response({"detail": "Delivery profile does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({"detail": "User does not have a delivery profile."}, status=status.HTTP_400_BAD_REQUEST)
                
    @action(detail=True, methods=['post'], url_path='supplier-accept')
    def supplier_accept(self, request, pk=None):
        return_request = self.get_object()
        user = request.user

        # Check if the user is a supplier
        if not hasattr(user, 'supplier'):
            return Response({'detail': 'You are not authorized to accept return requests.'}, status=status.HTTP_403_FORBIDDEN)


        if return_request.product.Supplier.user != user:
            return Response({'detail': 'This return request does not belong to you.'}, status=status.HTTP_403_FORBIDDEN)


        with transaction.atomic():
            warehouse = Warehouse.objects.get(name = return_request.to_state)
            return_amount = return_request.amount
            return_request.user.balance += return_amount
            user.Supplier.user.balance -= (return_amount + return_request.order.delivery_fee )

            return_request.user.save()
            user.supplier.save()
            transactions.objects.create(user=return_request.user,transaction_type = transactions.TransactionType.RETURNED_PRODUCT
                                        , amount=return_amount)
            transactions.objects.create(user=user, transaction_type = transactions.TransactionType.RETURNED_PRODUCT
                                        , amount= -(return_amount + return_request.order.delivery_fee))

            return_request.status = ReturnRequest.OrderStatus.ACCEPTED
            return_request.save()

        return Response({'status': 'Return request accepted and balances updated'})
    
    @action(detail=True, methods=['post'], url_path='supplier-reject')
    def supplier_reject(self, request, pk=None):
        return_request = self.get_object()
        user = request.user

        if not hasattr(user, 'supplier'):
            return Response({'detail': 'You are not authorized to reject return requests.'}, status=status.HTTP_403_FORBIDDEN)

        if return_request.product.Supplier.user != user:
            return Response({'detail': 'This return request does not belong to you.'}, status=status.HTTP_403_FORBIDDEN)

        return_request.status =  ReturnRequest.OrderStatus.REJECTED
        return_request.save()

        return Response({'status': 'Return request rejected'})   
    
    @action(detail=True, methods=['post'], url_path='cancel', url_name='cancel-order')
    def cancel_order(self, request, pk=None):
        try:
            user = request.user
            Return_Request = ReturnRequest.objects.get(pk=pk, user=user)
            if Return_Request.user != user:
                return Response({"detail": "You do not have permission to cancel this ReturnRequest."}, status=status.HTTP_403_FORBIDDEN)
            Return_Request.status = ReturnRequest.OrderStatus.CANCELLED
            Return_Request.save()
            return Response({"detail": "ReturnRequest has been cancelled."}, status=status.HTTP_200_OK)
        except ReturnRequest.DoesNotExist:
            return Response({"detail": "ReturnRequest not found."}, status=status.HTTP_404_NOT_FOUND)        
                    
class BalanceWithdrawRequestListCreateView(generics.ListCreateAPIView):
    queryset = Balance_Withdraw_Request.objects.all()
    serializer_class = BalanceWithdrawRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        transfer_type =self.request.data.get("transfer_type")
        amount = self.request.data.get("amount")
        
        if user.Balance < int(amount):
            raise serializers.ValidationError("Insufficient balance for this withdrawal.")
        with transaction.atomic():
            user.Balance -= int(amount)
            transactions.objects.create(user=self.request.user,transaction_type = transactions.TransactionType.WITHDRAW, amount=amount)
       
        user.save()

        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(f"your Withdrawal Request has been Created , you will receive Your amount Soon {serializer.data} ", status=status.HTTP_201_CREATED, headers=headers)
   
class BalanceWithdrawRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Balance_Withdraw_Request.objects.all()
    serializer_class = BalanceWithdrawRequestSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
def get_user_transactions(request):
    transactions_data = transactions.objects.filter(user=request.user)
    serializer = TransactionSerializer(transactions_data, many=True)
    return Response(serializer.data)