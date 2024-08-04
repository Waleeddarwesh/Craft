from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from orders.models import Order
from .serializers import OrderInformationSerializer,CourseInformationSerializer
from course.serializers import CourseSerializer
from course.models import Course ,Enrollment,Customer
from . import webhook

payment_type = None
class PaymentViewSet(viewsets.ViewSet):
    def get_serializer_class(self):
        if self.action == "process_payment":
            return OrderInformationSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["post"])
    def process_payment(self, request):
        serializer = OrderInformationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_id = serializer.validated_data["order_id"]
        order = get_object_or_404(Order, id=order_id)

        success_url = request.build_absolute_uri(reverse("payment:success"))
        cancel_url = request.build_absolute_uri(reverse("payment:cancel"))

        # Stripe checkout session data
        session_data = {
            "mode": "payment",
            "client_reference_id": order.id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }
        # add order items to the Stripe checkout session
        for item in order.items.all():
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(item.price * Decimal("100")),
                        "currency": "EGP",
                        "product_data": {
                            "name": item.product.ProductName,
                        },
                       
                    },
                    "quantity": item.quantity,
                    
                }
            )

        delivery_fee = order.delivery_fee if order.delivery_fee else Decimal("0.00")
        if delivery_fee > 0:
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(delivery_fee * Decimal("100")),
                        "currency": "EGP",
                        "product_data": {
                            "name": "Delivery Fee",
                        },
                    },
                    "quantity": 1,
                }
            )
        payment_type="Order"
        session = stripe.checkout.Session.create(**session_data)
        return Response({"status": "success", "url": session.url})
    
class CoursePaymentViewSet(viewsets.ViewSet):
    def get_serializer_class(self):
        if self.action == "process_payment":
            return CourseInformationSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["post"])
    def process_payment(self, request):
        serializer = CourseInformationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, CourseID=course_id)
        
        success_url = request.build_absolute_uri(reverse("payment:success"))
        cancel_url = request.build_absolute_uri(reverse("payment:cancel"))

        # Stripe checkout session data
        session_data = {
            "mode": "payment",
            "client_reference_id": course.CourseID,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [{
                "price_data": {
                    "unit_amount": int(course.Price * Decimal("100")),
                    "currency": "EGP",
                    "product_data": {
                        "name": course.CourseTitle,
                    },
                },
                "quantity": 1,
            }],
        }
  
        session = stripe.checkout.Session.create(**session_data)
        return Response({"status": "success", "url": session.url})

@api_view(['GET'])
def payment_completed(request):
    webhook.stripe_webhook(request)
    return Response("successed", status=status.HTTP_202_ACCEPTED)

@api_view(['GET'])
def payment_canceled(request):
    return Response( "your payment cancelled and your payment method will change into Cash on Delivery", status=status.HTTP_406_NOT_ACCEPTABLE)




