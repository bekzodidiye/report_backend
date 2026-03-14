from rest_framework import serializers
from apps.promises.models import Promise

class PromiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promise
        fields = ('id', 'title', 'description', 'status', 'deadline', 'created_at')
        read_only_fields = ('id', 'status', 'created_at')
