# medsafe/routing.py
from django.urls import path
from .consumer import NotificationConsumer  # 너가 만든 consumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
