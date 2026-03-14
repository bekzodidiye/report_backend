from rest_framework import serializers
from apps.problems.models import Problem

class ProblemSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Problem
        fields = ('id', 'institution', 'user', 'author_email', 'category', 'description', 
                  'photo', 'status', 'verification_count', 'created_at')
        read_only_fields = ('user', 'status', 'verification_count', 'created_at')

class ProblemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ('institution', 'category', 'description', 'photo')

    def validate_photo(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Photo size cannot exceed 5MB")
        return value
