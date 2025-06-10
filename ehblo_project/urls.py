# ehblo_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')), # User authentication and profiles
    path('courses/', include('courses.urls')), # Course management
    path('payments/', include('payments.urls')), # Payment processing
    path('', include('core.urls')), # Home page and other general pages
]

# Serve media files in development. In production, use a dedicated web server (Nginx/Apache) or cloud storage (S3).
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)