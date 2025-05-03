# prescriptions/admin.py

from django.contrib import admin
from .models import Prescription, Medication

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'created_at',
    )
    list_filter = ('created_at',)
    search_fields = ('ocr_text',)

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'prescription',
        'name',
        'frequency_per_day',
        'dosage',
        'pharmacy_name',
        'hospital_name',
        'pharmacy_phone',
        'categories',
    )
    list_filter = ('frequency_per_day', 'pharmacy_name', 'hospital_name',)
    search_fields = ('name', 'pharmacy_name', 'hospital_name',)
