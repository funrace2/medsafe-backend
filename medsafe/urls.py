"""
URL configuration for medsafe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# medsafe/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views as drf_views
from core.views import RegisterAPI

urlpatterns = [
    # 토큰 조회 (POST: username, password → token 반환)
    path('api-token-auth/', drf_views.obtain_auth_token),
    path('admin/', admin.site.urls),
    path('api/', include('prescriptions.urls')),
    # DRF 세션 로그인/로그아웃 뷰
    path('api-auth/', include('rest_framework.urls')),
    # core 앱 profile API
    path("api/", include("core.urls")),
    path('api/chat/', include('chat.urls')),
]
