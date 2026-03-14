from rest_framework import serializers
from apps.reports.models import Report

class ReportSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Report
        fields = ('id', 'institution', 'user', 'author_email', 'promise', 'promise_status', 
                  'photo', 'comment', 'status', 'verification_count', 'created_at')
        read_only_fields = ('user', 'status', 'verification_count', 'created_at')

    def validate_photo(self, value):
        from django.core.exceptions import ValidationError
        if value.size > 5 * 1024 * 1024:
            raise ValidationError("File size too large (max 5MB)")
        return value

class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('institution', 'promise', 'promise_status', 'photo', 'comment')

    def validate_photo(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Photo size cannot exceed 5MB")
        return value
