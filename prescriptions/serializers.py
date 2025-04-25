# prescriptions/serializers.py

from rest_framework import serializers
from .models import Prescription, Medication

class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = [
            'id',
            'name',
            'frequency_per_day',
            'dosage',
        ]


class PrescriptionSerializer(serializers.ModelSerializer):
    medications = MedicationSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id',
            'image',
            'ocr_text',
            'pharmacy_name',
            'pharmacy_phone',
            'hospital_name',
            'created_at',
            'medications',
        ]
        read_only_fields = ['ocr_text', 'created_at']
