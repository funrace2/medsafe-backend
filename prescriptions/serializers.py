# prescriptions/serializers.py

from rest_framework import serializers
from .models import Prescription, Medication, Allergy

class MedicationSerializer(serializers.ModelSerializer):
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
    interaction_warnings = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            "id",
            "user",
            "image",
            "ocr_text",
            "created_at",
            "medications",
            "interaction_warnings",
        ]
        read_only_fields = ["id", "ocr_text", "created_at", "medications"]
    def get_interaction_warnings(self, pres):
        meds = pres.medications.all()
        warnings = []

        # 1) 약물 간 상호작용 텍스트 활용
        #    - interaction 필드에 "A와 B 병용 시 ..." 같은 문장이 들어있다면 그대로 노출
        for m in meds:
            if m.interaction:
                warnings.append(f"{m.name} 상호작용: {m.interaction}")

        # 2) 주의사항–알레르기 활용
        #    - precautions 필드에 “○○ 금기” 식으로 주의사항이 들어있으면 그대로 노출
        user = self.context['request'].user
        allergic = Allergy.objects.filter(user=user).values_list('substance', flat=True)

        for m in meds:
            # 전체 주의사항 문단 중 유저 알레르기 물질이 언급된 문장만 뽑기
            if m.precautions:
                for sentence in m.precautions.split('.'):
                    for sub in allergic:
                        if sub in sentence:
                            warnings.append(f"알레르기 주의 ({m.name}): {sentence.strip()}")

        # 3) 약물 간 실제 병용 체크 (옵션)
        #    - 예: m1.interaction 안에 m2.name이 언급되면 “A와 B 병용 시 주의” 식으로 추가
        for m1 in meds:
            if m1.interaction:
                for m2 in meds:
                    if m2 == m1: continue
                    if m2.name in m1.interaction:
                        warnings.append(
                            f"{m1.name} ↔ {m2.name}: {m1.interaction}"
                        )

        return warnings
