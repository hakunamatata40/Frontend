# chat/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class ChatRoom(models.Model):
    # This links a chat room directly to a specific Course.
    # Using 'courses.Course' as a string prevents circular imports.
    course = models.OneToOneField(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='chat_room',
        unique=True, # Ensures only one chat room per course
    )

    class Meta:
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"

    def __str__(self):
        return f"Chat for Course: {self.course.title}"

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp'] # Newest messages at the bottom
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f'{self.sender.username} ({self.timestamp.strftime("%H:%M")}): {self.content[:50]}...'