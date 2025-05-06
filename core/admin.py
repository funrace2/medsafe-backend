# core/admin.py
from django.contrib import admin
from .models import Profile
from rest_framework.authtoken.models import Token

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'birth_date', 'gender', 'chronic_diseases', 'created_at')
    readonly_fields = ('token',)
    def token(self, obj):
        # Profile이 연결된 User에 Token이 있으면 key 반환, 없으면 빈 문자열
        try:
            return obj.user.auth_token.key
        except Token.DoesNotExist:
            return '-'
    token.short_description = 'Auth Token'
    list_filter  = ('gender',)
    search_fields = ('user__username', 'name')
