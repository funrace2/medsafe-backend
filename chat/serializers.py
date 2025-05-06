# chat/serializers.py

from rest_framework import serializers
from prescriptions.models import Medication

class ChatProxySerializer(serializers.Serializer):
    session_id = serializers.IntegerField(required=False)
    message    = serializers.CharField()

class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    author     = serializers.CharField()
    content    = serializers.CharField()

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        # 반환하고 싶은 필드만 골라서 나열
        fields = [
            'id',
            'name',
            'dosage',
            'frequency_per_day',
            'manufacturer',
            'efficacy',
            'usage',
            'warning',
            'precautions',
            'interaction',
            'side_effects',
            'storage',
            'image_url',
            'categories',
            'allergy_warnings',
            'condition_warnings',
        ]