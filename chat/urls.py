# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL for the main chat interface (e.g., /chat/1/ for course ID 1)
    path('<int:course_id>/', views.CourseChatView.as_view(), name='course_chat_detail'),

    # API endpoint to fetch messages (e.g., /chat/1/messages/)
    path('<int:course_id>/messages/', views.GetChatMessagesView.as_view(), name='get_chat_messages'),

    # API endpoint to send messages (e.g., /chat/1/send/)
    path('<int:course_id>/send/', views.PostChatMessageView.as_view(), name='post_chat_message'),
]