# core/serializers.py
from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class ProfileSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source='auth_token', read_only=True)
    class Meta:
        model = Profile
        fields = ['name', 'token', 'birth_date', 'gender', 'allergies', 'chronic_diseases', 'created_at', 'updated_at',]
        read_only_fields = ['created_at', 'updated_at', 'token']
