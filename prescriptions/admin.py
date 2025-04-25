# prescriptions/admin.py

from django.contrib import admin
from .models import Prescription, Medication

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'pharmacy_name',
        'hospital_name',
        'created_at',
    )
    list_filter = ('pharmacy_name', 'hospital_name', 'created_at')
    search_fields = ('pharmacy_name', 'hospital_name', 'ocr_text')

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'prescription',
        'name',
        'frequency_per_day',
        'dosage',
    )
    list_filter = ('frequency_per_day',)
    search_fields = ('name',)
