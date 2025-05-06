# core/views.py

from rest_framework import generics, permissions, viewsets
from rest_framework.permissions import AllowAny
from .models import Profile
from .serializers import ProfileSerializer, UserRegisterSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class RegisterAPI(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]  # 모든 사용자에게 허용
    def create(self, request, *args, **kwargs):
        # 1) User 생성
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 2) Token 발급
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "user_id": user.id,
            "username": user.username,
            "token": token.key
        })
    

class ProfileDetailAPI(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ProfileSerializer

    def get_object(self):
        # 로그인한 유저의 프로필만 조회/수정
        return self.request.user.profile
    
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [AllowAny]  # 모든 사용자에게 허용

    def get_queryset(self):
        # 토큰 인증된 유저 본인의 프로필만
        return Profile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # user FK 에 반드시 request.user 를 할당
        serializer.save(user=self.request.user)