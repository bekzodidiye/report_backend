from rest_framework import serializers
from .models import ConstructionReport


class ConstructionReportCreateSerializer(serializers.ModelSerializer):
    """Foydalanuvchi yuboriladigan ma'lumotlar validatsiyasi."""

    image = serializers.ImageField(required=False, write_only=True,
                                   help_text="jpg/png, max 5 MB")

    class Meta:
        model  = ConstructionReport
        fields = [
            'title', 'description', 'institution',
            'severity', 'latitude', 'longitude',
            'user_id', 'image',
        ]

    def validate_description(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters.")
        if len(value) > 2000:
            raise serializers.ValidationError("Description cannot exceed 2000 characters.")
        return value

    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate_image(self, value):
        allowed_types = ['image/jpeg', 'image/png']
        if hasattr(value, 'content_type') and value.content_type not in allowed_types:
            raise serializers.ValidationError("Only jpg/png files are allowed.")
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size cannot exceed 5 MB.")
        return value


class ConstructionReportListSerializer(serializers.ModelSerializer):
    """Ro'yxat uchun qisqa representation."""

    class Meta:
        model  = ConstructionReport
        fields = [
            'id', 'title', 'severity', 'status',
            'latitude', 'longitude', 'address_name',
            'view_count', 'like_count',
            'image_url', 'thumbnail_url',
            'created_at',
        ]


class ConstructionReportDetailSerializer(serializers.ModelSerializer):
    """Batafsil representation — barcha maydonlar."""

    institution_name = serializers.CharField(
        source='institution.name', read_only=True, default=None
    )
    institution_type = serializers.CharField(
        source='institution.type', read_only=True, default=None
    )

    class Meta:
        model  = ConstructionReport
        fields = [
            'id', 'user_id',
            'title', 'description',
            'institution', 'institution_name', 'institution_type',
            'severity', 'status',
            'latitude', 'longitude', 'address_name',
            'view_count', 'like_count',
            'image_url', 'thumbnail_url',
            'created_at', 'updated_at',
        ]


class ConstructionStatusUpdateSerializer(serializers.Serializer):
    """PATCH /status uchun validatsiya."""

    status = serializers.ChoiceField(
        choices=['APPROVED', 'REJECTED', 'RESOLVED'],
        help_text="New status value"
    )
