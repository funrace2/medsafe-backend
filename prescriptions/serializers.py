# prescriptions/serializers.py

from rest_framework import serializers
from .models import Prescription, Medication

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = [
            "id",
            "name",
            "dosage",
            "frequency_per_day",
            "entp_name",
            "efcy_qesitm",
            "use_method_qesitm",
            "atpn_warn_qesitm",
            "atpn_qesitm",
            "intrc_qesitm",
            "se_qesitm",
            "deposit_method_qesitm",
            "item_image",
            "created_at",
            "updated_at",
        ]


class PrescriptionSerializer(serializers.ModelSerializer):
    # user 필드는 요청한 사용자로 자동 설정되고, 클라이언트에서 받지 않음
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Prescription
        fields = [
            "id",
            "user",
            "image",
            "ocr_text",
            "pharmacy_name",
            "pharmacy_phone",
            "hospital_name",
            "created_at",
            "medications",
        ]
        read_only_fields = ["id", "ocr_text", "created_at", "medications"]
