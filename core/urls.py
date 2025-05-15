# core/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import RegisterAPI, ProfileViewSet, ProfileDetailAPI

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('profile/me/', ProfileDetailAPI.as_view(), name='my-profile'),
    path('', include(router.urls)),
]
