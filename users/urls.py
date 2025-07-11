# users/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # Import Django's default auth views
from .views import SignUpView, CustomLoginView, ProfileView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'), # Redirect to home after logout

    # Password Reset/Change (using Django's default views and templates)
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='users/registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/registration/password_change_done.html'), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/registration/password_reset_form.html', email_template_name='users/registration/password_reset_email.html', subject_template_name='users/registration/password_reset_subject.txt'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/registration/password_reset_complete.html'), name='password_reset_complete'),

    path('profile/', ProfileView.as_view(), name='profile'),
]