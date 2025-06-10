# payments/views.py
import stripe
import json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Transaction
from courses.models import Course, Enrollment
from users.models import CustomUser

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout_view(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_published=True)

    if request.user.user_type != 'student':
        messages.error(request, "Only students can purchase courses.")
        return redirect('course_detail', pk=course.id, slug=course.slug)

    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('my_courses')

    if course.price == 0:
        messages.info(request, "This is a free course. Please use the enroll button.")
        return redirect('course_detail', pk=course.id, slug=course.slug)

    if request.method == 'POST':
        try:
            # Create a Stripe PaymentIntent
            # Use 'manual' capture_method if you want to review payments before completing
            intent = stripe.PaymentIntent.create(
                amount=int(course.price * 100), # Amount in cents
                currency='usd', # Or your local currency, e.g., 'xaf'
                metadata={'course_id': course.id, 'user_id': request.user.id},
                description=f"Purchase of course: {course.title}",
                receipt_email=request.user.email,
                automatic_payment_methods={'enabled': True},
            )
            
            # Create a pending transaction record in your DB
            Transaction.objects.create(
                user=request.user,
                course=course,
                amount=course.price,
                currency='usd',
                stripe_charge_id=intent.id, # Store intent ID here temporarily
                status='pending'
            )

            return JsonResponse({'clientSecret': intent.client_secret})

        except stripe.error.StripeError as e:
            messages.error(request, f"Stripe error: {e.user_message}")
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")
            return JsonResponse({'error': str(e)}, status=500)

    context = {
        'course': course,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payments/checkout.html', context)


@csrf_exempt # CSRF protection is handled by Stripe's webhook signature verification
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        with transaction.atomic():
            # Update the transaction status in your DB
            try:
                # Find the transaction using the payment_intent.id
                # Ensure you stored payment_intent.id in stripe_charge_id field
                db_transaction = Transaction.objects.get(stripe_charge_id=payment_intent.id)
                db_transaction.status = 'succeeded'
                db_transaction.save()

                # Enroll the user in the course
                course_id = payment_intent['metadata'].get('course_id')
                user_id = payment_intent['metadata'].get('user_id')

                if course_id and user_id:
                    course = Course.objects.get(id=course_id)
                    user = CustomUser.objects.get(id=user_id)
                    
                    if not Enrollment.objects.filter(student=user, course=course).exists():
                        Enrollment.objects.create(student=user, course=course)
                        print(f"User {user.username} successfully enrolled in {course.title}")
                    else:
                        print(f"User {user.username} was already enrolled in {course.title}")
                else:
                    print("Webhook: Missing course_id or user_id in metadata.")

            except Transaction.DoesNotExist:
                print(f"Webhook: Transaction with ID {payment_intent.id} not found in DB.")
            except Course.DoesNotExist:
                print(f"Webhook: Course with ID {payment_intent['metadata'].get('course_id')} not found.")
            except CustomUser.DoesNotExist:
                print(f"Webhook: User with ID {payment_intent['metadata'].get('user_id')} not found.")
            except Exception as e:
                print(f"Webhook error during atomic transaction: {e}")

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        with transaction.atomic():
            try:
                db_transaction = Transaction.objects.get(stripe_charge_id=payment_intent.id)
                db_transaction.status = 'failed'
                db_transaction.save()
                print(f"PaymentIntent failed: {payment_intent.id}")
            except Transaction.DoesNotExist:
                print(f"Webhook: Failed Transaction with ID {payment_intent.id} not found in DB.")
            except Exception as e:
                print(f"Webhook error updating failed transaction: {e}")

    # ... handle other event types if necessary

    return HttpResponse(status=200)

@login_required
def payment_success_view(request):
    # This view is hit after Stripe payment completion (redirect from client-side)
    # The actual enrollment logic should primarily rely on webhooks for reliability
    # This is just a confirmation page.
    messages.success(request, "Payment successful! You have been enrolled in the course.")
    return render(request, 'payments/success.html')

@login_required
def payment_cancel_view(request):
    messages.warning(request, "Payment was cancelled or failed. Please try again.")
    return redirect('my_courses') # Or redirect to checkout again