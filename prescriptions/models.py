# prescriptions/models.py

from django.db import models
from django.conf import settings

class Prescription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    image = models.ImageField(
        upload_to='prescriptions/images/',
        help_text='약 봉투 사진'
    )
    ocr_text = models.TextField(
        blank=True,
        help_text='OCR로 읽어온 원문 텍스트'
    )
    pharmacy_name = models.CharField(
        max_length=100,
        help_text='약국 이름'
    )
    pharmacy_phone = models.CharField(
        max_length=20,
        help_text='약국 전화번호'
    )
    hospital_name = models.CharField(
        max_length=100,
        help_text='병원 이름'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='처방전 등록 일시'
    )

    def __str__(self):
        return f"{self.pharmacy_name} 처방전 ({self.created_at:%Y-%m-%d})"


class Medication(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='medications'
    )
    name = models.CharField(
        max_length=100,
        help_text='약 이름'
    )
    frequency_per_day = models.PositiveSmallIntegerField(
        help_text='1일 투여 횟수'
    )
    dosage = models.CharField(
        max_length=50,
        help_text='1회 투여량 (예: "1정", "5ml")'
    )

    def __str__(self):
        return f"{self.name} - {self.frequency_per_day}회/일"
