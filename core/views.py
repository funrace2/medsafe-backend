# core/views.py

from rest_framework import generics, permissions, viewsets
from .models import Profile
from .serializers import ProfileSerializer

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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
