from .models import CartItems,Cart, DeliveryOrder,Order, OrderItem,Warehouse
from .serializers import *
from rest_framework.response import Response
from rest_framework import status ,permissions
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from rest_framework import mixins, status, viewsets ,generics
from rest_framework.permissions import IsAuthenticated
from accounts.models import Address
from django.db.models import F
from django.utils import timezone
from rest_framework.decorators import action
from accounts.models import Delivery
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from returnrequest.models import transactions
from .permissions import DeliveryContractProvided

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        user = self.request.user
        existing_whishlist = Wishlist.objects.filter(user=user).first()
        if existing_whishlist:
            raise ValidationError("A whishlist already exists for this user")
        data=serializer.save(user=user)
        return Response({"message": "whishlist created successfully"}, status=status.HTTP_201_CREATED)
    
class WishlistItemViewSet(viewsets.ModelViewSet):
    permission_classes= [permissions.IsAuthenticated]
    queryset = WishlistItem.objects.all()
    serializer_class = WishlistItemSerializer

    def get_queryset(self):
        user = self.request.user
        return WishlistItem.objects.filter(wishlist__user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return AddWishlistItemSerializer

        return WishlistItemSerializer

    def perform_create(self, serializer):
        user = self.request.user
        # Check if the user has a wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        # If a new wishlist is created, set it in the serializer
        if created:
            serializer.save(user=user, wishlist=wishlist)
        else:
            # If user already has a wishlist, just save the item with that wishlist
            serializer.save(user=user, wishlist=wishlist)

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    
    def get_queryset(self):
        return Cart.objects.filter(User=self.request.user)
    
    def perform_create(self, serializer):
        user = self.request.user
        existing_cart = Cart.objects.filter(User=user).first()
        if existing_cart:
            raise ValidationError("A cart already exists for this user")
        data=serializer.save(User=user)
        return Response({"message": "Cart created successfully"}, status=status.HTTP_201_CREATED)
    
class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes= [permissions.IsAuthenticated]
    queryset = CartItems.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        user = self.request.user
        return CartItems.objects.filter(CartID__User=user)

    def get_serializer_class(self):
        if self.action == "create":
            return AddCartItemSerializer
        elif self.action == "update":
            return UpdateCartItemSerializer

        return CartItemSerializer

    def perform_create(self, serializer):
        user = self.request.user
        # Check if the user has a cart
        cart, created = Cart.objects.get_or_create(User=user)
        # If a new cart is created, set it in the serializer
        if created:
            serializer.save(user=user, CartID=cart)
        else:
            # If user already has a cart, just save the item with that cart
            serializer.save(user=user, CartID=cart)

Craft = User.objects.get(email = "CraftEG@Craft.com")      
class OrderViewSet(mixins.CreateModelMixin,mixins.RetrieveModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    serializer_class = OrderCreateSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_delivery:
                try:
                    return Order.objects.filter(
                        Q(from_state=user.delivery.governorate) & 
                        (Q(delivery_orders__delivery_person=user) | Q(delivery_orders__isnull=True)) &
                        ~Q(status__in=[Order.OrderStatus.DELIVERED_SUCCESSFULLY, Order.OrderStatus.ON_MY_WAY, Order.OrderStatus.DELIVERED_TO_First_WAREHOUSE,Order.OrderStatus.CANCELLED,Order.OrderStatus.In_Transmit])
                        )
                except ObjectDoesNotExist:
                    return Order.objects.none() 
            else:
                return Order.objects.filter(user=user).exclude(initial_status=Order.OrderStatus.In_Transmit).exclude(total_amount=0)
        return Order.objects.none()
    
    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(User=request.user)
        address_id = request.data.get("address_id")
        coupon_code = request.data.get("coupon_code")
        payment_method = request.data.get("payment_method")

        if not address_id:
            return Response({"detail": "Address ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        address = Address.objects.filter(user=request.user, id=address_id).first()
        if not address:
            return Response({"detail": "Address not found."}, status=status.HTTP_400_BAD_REQUEST)

        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty. Cannot create order."}, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            # Check if entered quantity is greater than or equal to stock
            cart_items = CartItems.objects.filter(CartID=cart)
            for cart_item in cart_items:
                if cart_item.Quantity > cart_item.Product.Stock:
                    return Response({"detail": f"Quantity of {cart_item.Product.ProductName} exceeds available stock."}, status=status.HTTP_400_BAD_REQUEST)
            
            Suppliers_id = set()
            for cart_item in cart_items:
                supplier_id = cart_item.Product.Supplier.user.id
                Suppliers_id.add(supplier_id)

            Supplier_states = set()
            supplier_addresses = {}
            for id in Suppliers_id:
                try:
                    addresses = Address.objects.filter(user=id)
                    state_number = addresses.count()
                    if state_number >1:
                        Response({"detail": f"Multiple Addresses found for supplier with ID {id}."},status=status.HTTP_400_BAD_REQUEST)
                    else:
                        state = addresses.first().State
                        supplier_addresses[id] = addresses.first()  
                        Supplier_states.add(state)
                except Address.DoesNotExist:
                    Response({"detail": f"Address not found for supplier with ID {id}."},status=status.HTTP_400_BAD_REQUEST)
            Delivery_Fee = 0  
                    
            if len(Supplier_states) == 1 and len(Suppliers_id) == 1:
                From_State = list(Supplier_states)[0]
                To_State = address.State
                supplier_address = supplier_addresses[list(Suppliers_id)[0]]
                if From_State == To_State:
                    warehouse = Warehouse.objects.get(name =  From_State  )
                    order = Order.objects.create(
                        user=request.user,
                        supplier = supplier_address.user.supplier,
                        cart=cart,  
                        address=address,
                        from_state=list(Supplier_states)[0],
                        to_state=address.State,
                        from_address=supplier_address,
                        status = Order.OrderStatus.CREATED,
                        initial_status = Order.OrderStatus.CREATED,
                        payment_method=payment_method
                    )
                    Delivery_Fee += warehouse.delivery_fee
                else :
                    warehouse = Warehouse.objects.get(name = address.State)
                    order = Order.objects.create(
                        user=request.user,
                        supplier = supplier_address.user.supplier,
                        product=cart_item.Product,
                        address=address,
                        from_state=warehouse.Address.State,
                        to_state=address.State,
                        from_address=warehouse.Address,
                        status = Order.OrderStatus.In_Transmit,
                        initial_status = Order.OrderStatus.In_Transmit,
                        payment_method=payment_method
                    )
                    Delivery_Fee += warehouse.delivery_fee
                    related_order = order
                    warehouse = Warehouse.objects.get(name = list(Supplier_states)[0] )
                    order = Order.objects.create(
                        user=request.user,
                        supplier = supplier_address.user.supplier,
                        product=cart_item.Product,
                        address=warehouse.Address,
                        from_state=list(Supplier_states)[0],
                        to_state=warehouse.Address.State,
                        from_address=supplier_address,
                        status = Order.OrderStatus.CREATED,
                        initial_status = Order.OrderStatus.CREATED,
                        related_order= related_order,
                        payment_method=payment_method
                    )
                    Delivery_Fee += warehouse.delivery_fee +20
            
            elif len(Supplier_states) == 1 and len(Suppliers_id) > 1:
                warehouse = Warehouse.objects.get(name = list(Supplier_states)[0])
                for cart_item in cart_items:
                    supplier_id = cart_item.Product.Supplier.user.id
                    supplier_address = supplier_addresses[supplier_id]
                    order = Order.objects.create(
                        user=request.user,
                        supplier = supplier_id ,
                        product=cart_item.Product,
                        address=address,
                        from_state=list(Supplier_states)[0],
                        to_state=address.State,
                        from_address=supplier_address,
                        status = Order.OrderStatus.CREATED,
                        initial_status = Order.OrderStatus.CREATED,
                        payment_method=payment_method
                    )
                Delivery_Fee += warehouse.delivery_fee    
                   
            elif len(Supplier_states) > 1 and len(Suppliers_id) > 1:
                for cart_item in cart_items:
                    supplier_id = cart_item.Product.Supplier.user.id
                    supplier_address = supplier_addresses[supplier_id]
                    Supplier_State = supplier_address.State
                    To_State = address.State

                    if Supplier_State == To_State:
                        warehouse = Warehouse.objects.get(name = Supplier_State)
                        order = Order.objects.create(
                        user=request.user,
                        supplier = supplier_address.user.supplier ,
                        cart=cart,  
                        address=address,
                        from_state=Supplier_State,
                        to_state=address.State,
                        from_address=supplier_address,
                        status = Order.OrderStatus.CREATED,
                        initial_status = Order.OrderStatus.CREATED,
                        payment_method=payment_method
                    )
                        Delivery_Fee += warehouse.delivery_fee 
                    else:
                        warehouse = Warehouse.objects.get(name = address.State )
                        order = Order.objects.create(
                            user=request.user,
                            supplier = supplier_address.user.supplier ,
                            product=cart_item.Product,
                            address=address,
                            from_state=warehouse.Address.State,
                            to_state=address.State,
                            from_address=warehouse.Address,
                            status = Order.OrderStatus.In_Transmit,
                            initial_status = Order.OrderStatus.In_Transmit,
                            payment_method=payment_method
                            
                        )
                        Delivery_Fee += warehouse.delivery_fee
                        related_order = order
                        warehouse = Warehouse.objects.get(name = Supplier_State )
                        order = Order.objects.create(
                            user=request.user,
                            supplier = supplier_address.user.supplier,
                            product=cart_item.Product,
                            address=warehouse.Address,
                            from_state=Supplier_State,
                            to_state=warehouse.Address.State,
                            from_address=supplier_address,
                            status = Order.OrderStatus.CREATED,
                            initial_status = Order.OrderStatus.CREATED,
                            related_order= related_order,
                            payment_method=payment_method
                        )
                        Delivery_Fee += warehouse.delivery_fee + 20
                                       
            total_amount = 0
            discount_amount = 0
            discount_applied = False
            order_items = []
            for cart_item in cart_items:
                total_amount += cart_item.Product.UnitPrice * cart_item.Quantity
                order_item = OrderItem(
                    order=order,
                    product=cart_item.Product,
                    quantity=cart_item.Quantity,
                    price=cart_item.Product.UnitPrice
                )
                order_items.append(order_item)
                if coupon_code and not discount_applied:
                    try:
                        coupon = Coupon.objects.get(code=coupon_code, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
                        if any(cart_item.Product.Supplier == coupon.supplier for cart_item in cart_items):
                            discount_amount = (coupon.discount / 100) * total_amount
                            total_amount -= discount_amount
                            discount_applied = True  
                    except Coupon.DoesNotExist:
                        return Response({"detail": "Invalid or expired coupon."}, status=status.HTTP_400_BAD_REQUEST)

            OrderItem.objects.bulk_create(order_items)

            # Update order totals
            final_amount = total_amount - discount_amount
            order.total_amount = total_amount
            order.discount_amount = discount_amount
            order.delivery_fee = Delivery_Fee
            order.final_amount = final_amount + Delivery_Fee
            if payment_method == Order.PaymentMethod.BALANCE:
                user = request.user
                if user.Balance < order.final_amount:
                    order.payment_method = Order.PaymentMethod.CASH_ON_DELIVERY
                    return Response({"detail": "Insufficient balance for this order , your Payment Method will turn into Cash on Delivery."}
                                    , status=status.HTTP_400_BAD_REQUEST)
                user.Balance -= order.final_amount
                Craft.Balance += (order.final_amount)
                transactions.objects.create(user=order.user,transaction_type = transactions.TransactionType.PURCHASED_PRODUCTS
                                            , amount= -order.final_amount)
                transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.PURCHASED_PRODUCTS
                                            , amount= (order.final_amount))
                user.save()
                order.status = Order.OrderStatus.PAID
                order.paid = True
            order.save()
            cashback_amount = (order.final_amount) * 5/100
            transactions.objects.create(user=order.user,transaction_type = transactions.TransactionType.CASH_BACK
                                        , amount=cashback_amount)
            # Reduce product stock
            for cart_item in cart_items:
                cart_item.Product.Stock = F('Stock') - cart_item.Quantity
                cart_item.Product.save()

            cart_items.delete()
            request.session["order_id"] = str(order.id)
             # Send notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
            f"user_{request.user.id}",
            {
            "type": "order.created",
            "message": "Your order has been created."
             }
          )

        return Response({"message": "Order Created Successfully", "order_id": order.id, 
                         "Total amount" :order.total_amount,
                         "Discount amount":order.discount_amount,
                         "Deliverey Fee" : order.delivery_fee,
                         "final_amount": order.final_amount}
                        , status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return OrderListRetrieveSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['post'], url_path='accept', permission_classes=[IsAuthenticated, DeliveryContractProvided])
    def accept(self, request, pk=None):
        order = self.get_object()
        user = request.user
        
        # Check if the user is a delivery person
        if not user.is_delivery:
            return Response({'detail': 'You are not authorized to accept orders.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if the order is already accepted by another delivery person
        if hasattr(order, 'delivery_order') and order.delivery_order.delivery_person != user:
            return Response({'detail': 'This order has already been accepted by another delivery person.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update the DeliveryOrder entry
        delivery_order, created = DeliveryOrder.objects.get_or_create(order=order, defaults={'delivery_person': user})
        if not created and delivery_order.delivery_person != user:
            return Response({'detail': 'This order has already been accepted by another delivery person.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the order status
        order.status = Order.OrderStatus.ON_MY_WAY
        order.delivery = user.delivery
        order.save()
        
        return Response({'status': 'Order accepted and status updated to on my way'})
    
    @action(detail=True, methods=['post'], url_path='delivered')
    def delivered(self, request, pk=None):
        try:
            user = request.user
            order = Order.objects.get(pk=pk, delivery=user.delivery)
            
            if not user.is_delivery:
                return Response({"detail": "Only delivery persons can mark orders as delivered."}, status=status.HTTP_403_FORBIDDEN)
            
            try:
                delivery_order = DeliveryOrder.objects.get(order=order, delivery_person=user)
            except delivery_order.DoesNotExist:
                return Response({"detail": "This order is not accepted by you."}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = OrderDeliverSerializer(data=request.data)
            with transaction.atomic():
                if serializer.is_valid():
                    confirmation_code = serializer.validated_data.get('confirmation_code')
                    if confirmation_code != order.confirmation_code:
                        return Response({"detail": "Invalid confirmation code."}, status=status.HTTP_400_BAD_REQUEST)
                    warehouse = Warehouse.objects.get(name = user.delivery.governorate )
                    if order.related_order:
                        order.status = Order.OrderStatus.DELIVERED_SUCCESSFULLY
                        order.delivery_confirmed_at = timezone.now()
                        order.save()
                        if order.payment_method in[Order.PaymentMethod.BALANCE,Order.PaymentMethod.CREDIT_CARD]: 
                            user.Balance += (warehouse.delivery_fee-15/100*warehouse.delivery_fee)
                            Craft.Balance += (15/100*warehouse.delivery_fee)
                            order.supplier.user += (order.total_amount-15/100*order.total_amount)
                            Craft.Balance -= (order.total_amount)
                            transactions.objects.create(user=user,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                    , amount=(warehouse.delivery_fee-15/100*warehouse.delivery_fee))
                            transactions.objects.create(user=order.supplier.user,transaction_type = transactions.TransactionType.PURCHASED_PRODUCTS
                                                    , amount= (order.total_amount-15/100*order.total_amount))
                            transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                    , amount= (15/100*warehouse.delivery_fee))
                            transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.SUPPLIER_TRANSFORM
                                                    , amount= -(order.total_amount))
                        elif order.payment_method == Order.PaymentMethod.CASH_ON_DELIVERY:
                            Delivery_final_amount = order.final_amount - warehouse.delivery_fee
                            user.Balance -= Delivery_final_amount
                            order.supplier.user += (order.total_amount-15/100*order.total_amount)
                            Craft.Balance += (15/100*order.total_amount)
                            transactions.objects.create(user=user,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                    , amount= -Delivery_final_amount)
                            transactions.objects.create(user=order.supplier.user,transaction_type = transactions.TransactionType.PURCHASED_PRODUCTS
                                                    , amount= (order.total_amount-15/100*order.total_amount))
                            transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                    , amount= (15/100*order.total_amount))
                    else:
                        if order.cart:
                            if order.payment_method in[Order.PaymentMethod.BALANCE,Order.PaymentMethod.CREDIT_CARD]: 
                                user.Balance += (warehouse.delivery_fee-15/100*warehouse.delivery_fee)
                                Craft.Balance += (15/100*warehouse.delivery_fee)
                                order.supplier.user += (order.total_amount-15/100*order.total_amount)
                                Craft.Balance -= (order.total_amount)
                                transactions.objects.create(user=user,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                        , amount=(warehouse.delivery_fee-15/100*warehouse.delivery_fee))
                                transactions.objects.create(user=order.supplier.user,transaction_type = transactions.TransactionType.PURCHASED_PRODUCTS
                                                        , amount= (order.total_amount-15/100*order.total_amount))
                                transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                        , amount= (15/100*warehouse.delivery_fee))
                                transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.SUPPLIER_TRANSFORM
                                                        , amount= -(order.total_amount))
                            elif order.payment_method == Order.PaymentMethod.CASH_ON_DELIVERY:
                                Delivery_final_amount = order.final_amount - warehouse.delivery_fee
                                user.Balance -= Delivery_final_amount
                                order.supplier.user += (order.total_amount-15/100*order.total_amount)
                                Craft.Balance += (15/100*order.total_amount)
                                transactions.objects.create(user=user,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                        , amount= -Delivery_final_amount)
                                transactions.objects.create(user=order.supplier.user,transaction_type = transactions.TransactionType.PURCHASED_PRODUCTS
                                                        , amount= (order.total_amount-15/100*order.total_amount))
                                transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                        , amount= (15/100*order.total_amount))
                                
                        else:
                            order.status = Order.OrderStatus.DELIVERED_TO_First_WAREHOUSE
                            order.delivery_confirmed_at = timezone.now()
                            order.save()
                            user.Balance += (warehouse.delivery_fee-15/100*warehouse.delivery_fee)
                            Craft.Balance += (15/100*warehouse.delivery_fee)
                            transactions.objects.create(user=user,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                    , amount=(warehouse.delivery_fee-15/100*warehouse.delivery_fee))
                            transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.DELIVERY_FEE
                                                    , amount= (15/100*warehouse.delivery_fee))
                    
                    
                    return Response({'status': 'Order status updated to delivered successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='accepted_orders')
    def accepted_orders(self, request):
        try:
            # Ensure the user is a delivery person and access the related Delivery profile
            delivery_person = request.user
            delivery_profile = delivery_person.delivery
            # Filter orders accepted by the current delivery person
            orders = Order.objects.filter(
                delivery_orders__delivery_person=delivery_person,
                delivery_orders__accepted_at__isnull=False,
                status=Order.OrderStatus.ON_MY_WAY
            )
            serializer = self.get_serializer(orders, many=True)
            return Response(serializer.data)
        except Delivery.DoesNotExist:
            return Response({"detail": "Delivery profile does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({"detail": "User does not have a delivery profile."}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'], url_path='cancel', url_name='cancel-order')
    def cancel_order(self, request, pk=None):
        try:
            user = request.user
            order = Order.objects.get(pk=pk, user=user)
            
            if order.user != request.user:
                    return Response({"detail": "You do not have permission to cancel this order."}, status=status.HTTP_403_FORBIDDEN)
        
            if order.status in [Order.OrderStatus.CREATED ,Order.OrderStatus.PAID,Order.OrderStatus.In_Transmit] :
                order.status = Order.OrderStatus.CANCELLED
                order.save()
                if order.related_order:
                    related_order = order.related_order
                    related_order.status = Order.OrderStatus.CANCELLED
                    related_order.save()
                cashback_amount = (order.final_amount) * 5/100
                if order.payment_method == Order.PaymentMethod.BALANCE:
                        user.Balance += order.final_amount
                        user.Balance -= cashback_amount
                        transactions.objects.create(user=order.user,transaction_type = transactions.TransactionType.CASH_BACK
                                        , amount=-cashback_amount)
                        transactions.objects.create(user=user,transaction_type = transactions.TransactionType.RETURNED_PRODUCT
                                            , amount=(order.final_amount))
                        
                elif order.payment_method == Order.PaymentMethod.CREDIT_CARD and order.paid:
                        user.Balance += order.final_amount
                        user.Balance -= cashback_amount
                        transactions.objects.create(user=order.user,transaction_type = transactions.TransactionType.RETURNED_CASH_BACK
                                        , amount=-cashback_amount)
                        transactions.objects.create(user=user,transaction_type = transactions.TransactionType.RETURNED_PRODUCT
                                            , amount=(order.final_amount))
                elif order.payment_method == Order.PaymentMethod.CASH_ON_DELIVERY:
                        user.Balance -= cashback_amount
                        transactions.objects.create(user=order.user,transaction_type = transactions.TransactionType.RETURNED_CASH_BACK
                                        , amount=-cashback_amount)    

                return Response({"detail": "Order has been cancelled."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Cannot cancel an order that has been delivered or marked as failed delivery."}, status=status.HTTP_400_BAD_REQUEST)
        
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        
class OrdersHistoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderListRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_customer:
            out  = Order.objects.filter(user=self.request.user).exclude(initial_status=Order.OrderStatus.In_Transmit).exclude(total_amount=0)
        elif user.is_supplier:
            out = Order.objects.filter(supplier=self.request.user.supplier).exclude(initial_status=Order.OrderStatus.In_Transmit).exclude(total_amount=0)
        elif user.is_delivery:
            out = Order.objects.filter(delivery=self.request.user.delivery)
        return out
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class RturnOrdersProductsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = ReturnRequestListRetrieveSerializer  
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        fourteen_days_ago = timezone.now() - timezone.timedelta(days=14)

        if user.is_customer:
            queryset = Order.objects.filter(user=user, updated_at__gte=fourteen_days_ago)
        else:
            queryset = Order.objects.none()  # No orders for other types of users

        return queryset

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
            if self.request.user.is_supplier:
                 return Coupon.objects.filter(supplier=self.request.user.supplier)
            else:
                 return Coupon.objects.filter(active=True)

    def perform_create(self, serializer):
        coupon = serializer.save(supplier=self.request.user.supplier)
        supplier_products = Product.objects.filter(Supplier=self.request.user.supplier)
        coupon.products.set(supplier_products)
    
    def perform_update(self, serializer):
        supplier = self.request.user.supplier
        instance = self.get_object()

        # Ensure the coupon belongs to the current supplier
        if instance.supplier != supplier:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        # Update the coupon and associated products
        serializer.save()

        # Update products associated with the coupon if needed
        supplier_products = Product.objects.filter(Supplier=supplier)
        instance.products.set(supplier_products)

    def perform_destroy(self, instance):
        supplier = self.request.user.supplier

        # Ensure the coupon belongs to the current supplier
        if instance.supplier != supplier:
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)

        instance.delete()
        return Response({"detail": "Coupon deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class WarehouseListView(generics.ListAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer