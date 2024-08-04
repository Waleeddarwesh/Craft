import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from course.models import Course, Customer, Enrollment
from orders.models import Order,User
from returnrequest.models import transactions
stripe.api_key = settings.STRIPE_SECRET_KEY

Craft = User.objects.get(email = "CraftEG@Craft.com")
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get("Stripe-Signature")
    event = None
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == "checkout.session.completed":
        session = event['data']['object']
        
        if session['mode'] == "payment" and session['payment_status'] == "paid":
            client_reference_id = session['client_reference_id']
            
            if 'order' in client_reference_id:
                try:
                    order = Order.objects.get(id=client_reference_id['order'])
                    order.supplier.user.Balance += (order.total_amount-15/100*order.total_amount)
                    Craft.Balance+= (15/100*order.total_amount)
                    transactions.objects.create(user=customer.user,transaction_type = transactions.TransactionType.RETURNED_PRODUCT,
                                                 amount=(order.total_amount-15/100*order.total_amount))
                    transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.PURCHASED_PRODUCTS,
                                                 amount= (15/100*order.final_amount))
                    order.status = Order.OrderStatus.PAID
                    order.stripe_id = session['payment_intent']
                    order.save()
                    
                    return HttpResponse(status=200)
                except Order.DoesNotExist:
                    return HttpResponse(status=404)
            
            elif 'course' in client_reference_id:
                try:
                    course = Course.objects.get(CourseID=client_reference_id['course'])
                    customer_email = session['customer_email']
                    customer = Customer.objects.get(user__email=customer_email)
                    customer.user.Balance += (course.Price-15/100*course.Price)
                    Craft.Balance += 15/100*course.Price
                    transactions.objects.create(user=customer.user,transaction_type = transactions.TransactionType.PURCHASED_COURSE,
                                                 amount=(course.Price-15/100*course.Price))
                    transactions.objects.create(user=Craft,transaction_type = transactions.TransactionType.PURCHASED_COURSE,
                                                 amount= (15/100*course.Price))
                    Enrollment.objects.create(Course=course, Customer=customer)
                    
                    return HttpResponse(status=200)
                except (Course.DoesNotExist, Customer.DoesNotExist):
                    return HttpResponse(status=404)
    
    return HttpResponse(status=200)
