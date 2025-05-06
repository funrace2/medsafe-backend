# core/models.py

from django.conf import settings
from django.db import models

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    ]

    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,related_name='profile')
    name   = models.CharField("이름", max_length=100)
    birth_date  = models.DateField("생년월일")
    gender      = models.CharField("성별", max_length=1, choices=GENDER_CHOICES)
    allergies   = models.JSONField("알레르기 정보", blank=True, default=list)
    chronic_diseases = models.JSONField("만성 질환", blank=True, default=list)
    auth_token        = models.CharField("Auth Token", max_length=40, blank=True, null=True, editable=False, help_text="DRF 인증 토큰")

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        # user 가 설정되어 있으면 username, 없으면 "프로필 #<pk>" 로 표시
        if self.user:
            return f"{self.user.username}의 프로필"
        return f"프로필 #{self.pk}"
    