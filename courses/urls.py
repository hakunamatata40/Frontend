# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Public Course List & Detail
    path('', views.CourseListView.as_view(), name='course_list'),
    path('subject/<slug:subject_slug>/', views.CourseListView.as_view(), name='course_list_by_subject'),
    path('<int:pk>/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),

    # Instructor Dashboard & Course CRUD
    path('instructor-dashboard/', views.InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),
    path('<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),

    # Module CRUD
    path('<int:course_id>/module/create/', views.ModuleCreateUpdateView.as_view(), name='module_create'),
    path('<int:course_id>/module/<int:pk>/edit/', views.ModuleCreateUpdateView.as_view(), name='module_update'),
    path('<int:pk>/module/delete/', views.ModuleDeleteView.as_view(), name='module_delete'), # pk is module_id

    # Content CRUD (using generic relations)
    # E.g., /courses/1/module/2/content/add/textcontent/
    path('<int:module_id>/content/add/<str:model_name>/', views.ContentCreateUpdateView.as_view(), name='module_content_create'),
    # E.g., /courses/1/module/2/content/3/edit/textcontent/
    path('<int:module_id>/content/<int:pk>/edit/<str:model_name>/', views.ContentCreateUpdateView.as_view(), name='module_content_update'),
    path('<int:pk>/content/delete/', views.ContentDeleteView.as_view(), name='content_delete'), # pk is content_id

    # Content Ordering API
    path('<int:module_id>/content/order/', views.ContentOrderView.as_view(), name='content_order'),

    # Student Enrollment & Course Player
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('my-courses/', views.EnrolledCourseListView.as_view(), name='my_courses'),
    # Course Player URL: /my-courses/<enrollment_id>/module/<module_id>/content/<content_id>/
    path('my-courses/<int:enrollment_id>/', views.CoursePlayerView.as_view(), name='course_player_home'), # Start of course
    path('my-courses/<int:enrollment_id>/module/<int:module_id>/', views.CoursePlayerView.as_view(), name='course_player_module'),
    path('my-courses/<int:enrollment_id>/module/<int:module_id>/content/<int:content_id>/', views.CoursePlayerView.as_view(), name='course_player_content'),
]