#chat/urls.py

from django.urls import path
from .views import ChatProxyAPIView, UserMedicationAPIView

urlpatterns = [
    path('', ChatProxyAPIView.as_view(), name='chat-proxy'),
    #    GET /api/chat/medications/ 에 토큰 헤더를 달고 요청하면
    #    로그인한 유저의 Medication 리스트가 JSON으로 반환됩니다.
    path('medications/', UserMedicationAPIView.as_view(), name='user-medications'),
]