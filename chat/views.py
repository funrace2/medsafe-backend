# chat/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from prescriptions.models import Medication
from .serializers import ChatProxySerializer, ChatResponseSerializer, MedicationSerializer
from .models import ChatSession, ChatMessage
import requests
from django.conf import settings

class ChatProxyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1) 입력 검증
        serializer = ChatProxySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id = serializer.validated_data.get('session_id')
        text       = serializer.validated_data['message']

        # 2) ChatSession 가져오거나 새로 만들기
        if session_id:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user)

        # 3) 유저 메시지 저장
        ChatMessage.objects.create(session=session, author='user', content=text)

        # 4) 외부 챗봇 API 호출 (예시)
        resp = requests.post(
            settings.CHATBOT_API_URL,
            headers={'Authorization': f'Bearer {settings.CHATBOT_API_TOKEN}'},
            json={'session_id': session.id, 'text': text}
        )
        resp.raise_for_status()
        bot_reply = resp.json().get('reply')  # 팀원분이 정의한 키

        # 5) 봇 메시지 저장
        ChatMessage.objects.create(session=session, author='bot', content=bot_reply)

        # 6) 응답 포맷팅
        out = {
            'session_id': session.id,
            'author': 'bot',
            'content': bot_reply,
        }
        return Response(ChatResponseSerializer(out).data)
    
class UserMedicationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meds = Medication.objects.filter(prescription__user=request.user)
        serializer = MedicationSerializer(meds, many=True)
        return Response(serializer.data)