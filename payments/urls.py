# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('checkout/<int:course_id>/', views.checkout_view, name='checkout'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'), # Stripe webhook endpoint
    path('success/', views.payment_success_view, name='payment_success'),
    path('cancel/', views.payment_cancel_view, name='payment_cancel'),
]