# core/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import ProfileDetailAPI, ProfileViewSet

router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = router.urls
