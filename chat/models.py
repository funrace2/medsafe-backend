# chat/models.py

from django.conf import settings
from django.db import models

class ChatSession(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    session    = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    author     = models.CharField(max_length=50)   # 'user' or 'bot'
    content    = models.TextField()
    timestamp  = models.DateTimeField(auto_now_add=True)
