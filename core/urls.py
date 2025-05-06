# core/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RegisterAPI, ProfileViewSet

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('', include(router.urls)),
]
