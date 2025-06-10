# core/urls.py
from django.urls import path
from .views import HomePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    # Add other general pages like about, contact, terms, etc. here
    # path('about/', views.AboutPageView.as_view(), name='about'),
]