# core/models.py

from django.conf import settings
from django.db import models

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    ]

    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name   = models.CharField("이름", max_length=100)
    birth_date  = models.DateField("생년월일")
    gender      = models.CharField("성별", max_length=1, choices=GENDER_CHOICES)
    allergies   = models.JSONField("알레르기 정보", blank=True, default=list)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} 프로필"
