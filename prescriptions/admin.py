# prescriptions/admin.py

from django.contrib import admin
from .models import Prescription, Medication, CalendarMemo

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
        'interaction_warnings',
        'allergy_warnings',
        'condition_warnings',
    )
    list_filter = ('frequency_per_day', 'pharmacy_name', 'hospital_name','interaction_warnings',)
    search_fields = ('name', 'pharmacy_name', 'hospital_name','interaction_warnings',)

@admin.register(CalendarMemo)
class CalendarMemoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'date',
        'content',
        'created_at',
    )
    list_filter = ('date',)
    search_fields = ('content',)