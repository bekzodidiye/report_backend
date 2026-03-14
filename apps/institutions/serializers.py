from rest_framework import serializers
from apps.institutions.models import Institution
from apps.promises.serializers import PromiseSerializer
from apps.problems.serializers import ProblemSerializer

class InstitutionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ('id', 'name', 'type', 'region', 'district', 'latitude', 'longitude', 'status')

class InstitutionDetailSerializer(serializers.ModelSerializer):
    promises = PromiseSerializer(many=True, read_only=True)
    recent_problems = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = ('id', 'external_id', 'name', 'type', 'region', 'district', 'address', 
                  'latitude', 'longitude', 'status', 'promises', 'recent_problems', 'created_at', 'updated_at')

    def get_recent_problems(self, obj):
        from apps.problems.models import Problem
        problems = Problem.objects.filter(institution=obj, status='verified')[:10]
        from apps.problems.serializers import ProblemSerializer
        return ProblemSerializer(problems, many=True).data
