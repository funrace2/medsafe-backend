# core/admin.py
from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'birth_date', 'gender', 'created_at')
    list_filter  = ('gender',)
    search_fields = ('user__username', 'name')
