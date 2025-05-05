# prescriptions/serializers.py

from rest_framework import serializers
from .models import Prescription, Medication

class MedicationSerializer(serializers.ModelSerializer):

    interaction_warnings = serializers.ListField(
        child=serializers.DictField(), read_only=True
    )
    allergy_warnings   = serializers.JSONField(read_only=True)
    condition_warnings = serializers.JSONField(read_only=True)
    class Meta:
        model = Medication
        fields = [
            "id",
            "name",
            "dosage",
            "frequency_per_day",
            "pharmacy_name",
            "pharmacy_phone",
            "hospital_name",
            "entp_name",
            "efcy_qesitm",
            "categories",
            "interaction_warnings",
            "allergy_warnings",
            "condition_warnings",
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
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "interaction_warnings",
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
            "created_at",
            "medications",
        ]
        read_only_fields = ["id", "ocr_text", "created_at", "medications",]
