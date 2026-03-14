from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'avatar', 'role', 'score', 'level', 'created_at')
        read_only_fields = ('id', 'role', 'score', 'level', 'created_at')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'phone')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'], # Using email as username
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone')
        )
        return user

class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'avatar', 'role', 'score', 'level')
        read_only_fields = ('id', 'email', 'role', 'score', 'level')
