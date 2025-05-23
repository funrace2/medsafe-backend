# prescriptions/models.py

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model

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
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='처방전 등록 일시'
    )
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"처방전 ({self.created_at:%Y-%m-%d})"


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
    pharmacy_name = models.CharField(
        "약국명",
        max_length=100,
        blank=True,
        null=True
    )
    pharmacy_phone = models.CharField(
        "약국 전화번호",
        max_length=20,
        blank=True,
        null=True
    )
    hospital_name = models.CharField(
        "병원 이름",
        max_length=100,
        blank=True,
        null=True
    )
    # --- e약은요 API에서 가져올 추가 정보들 ---
    manufacturer       = models.CharField( max_length=255, blank=True, null=True, help_text="entpName(업체명)" )
    efficacy           = models.TextField(    blank=True, null=True, help_text="efcyQesitm(효능)" )
    usage              = models.TextField(    blank=True, null=True, help_text="useMethodQesitm(사용법)" )
    warning            = models.TextField(    blank=True, null=True, help_text="atpnWarnQesitm(주의사항 경고)" )
    precautions        = models.TextField(    blank=True, null=True, help_text="atpnQesitm(주의사항)" )
    interaction        = models.TextField(    blank=True, null=True, help_text="intrcQesitm(상호작용)" )
    side_effects       = models.TextField(    blank=True, null=True, help_text="seQesitm(부작용)" )
    storage            = models.TextField(    blank=True, null=True, help_text="depositMethodQesitm(보관법)" )
    image_url          = models.URLField(     max_length=500, blank=True, null=True, help_text="itemImage(낱알이미지 URL)" )

    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)
    # --- 품목분류 API에서 가져올 추가 정보들 ---
    categories = ArrayField(models.CharField(max_length=100), default=list)

    interaction_warnings = models.JSONField(
        blank=True,
        default=list,
        help_text="[{new, old, keyword, score, direction}, …] 형태의 충돌 경고 리스트"
    )
    allergy_warnings   = models.JSONField("알러지 경고",    blank=True, default=list)
    condition_warnings = models.JSONField("지병 경고",     blank=True, default=list)

    
    def __str__(self):
        return f"{self.name} - {self.frequency_per_day}회/일"
    
User = get_user_model()

class CalendarMemo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"