from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.db.models import Count, Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.responses import standard_response
from apps.institutions.models import Institution
from apps.reports.models import Report
from apps.problems.models import Problem
from apps.users.models import User

class DashboardStatsView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['dashboard'])
    def get(self, request):
        stats = cache.get('dashboard_stats')
        if not stats:
            stats = {
                "total_institutions": Institution.objects.count(),
                "total_reports": Report.objects.count(),
                "verified_reports": Report.objects.filter(status='verified').count(),
                "total_problems": Problem.objects.count(),
                "verified_problems": Problem.objects.filter(status='verified').count(),
                "total_users": User.objects.count()
            }
            cache.set('dashboard_stats', stats, 60 * 5)
        return standard_response(data=stats)

class DashboardMapView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['dashboard'])
    def get(self, request):
        map_data = cache.get('dashboard_map')
        if not map_data:
            map_data = list(Institution.objects.values(
                'id', 'latitude', 'longitude', 'status', 'name'
            ))
            cache.set('dashboard_map', map_data, 60 * 5)
        return standard_response(data=map_data)

class TopUsersView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['dashboard'])
    def get(self, request):
        top_users = cache.get('dashboard_top_users')
        if not top_users:
            users = User.objects.order_by('-score')[:10]
            top_users = [
                {
                    "id": user.id,
                    "email": user.email,
                    "score": user.score,
                    "level": user.level,
                    "avatar": user.avatar.url if user.avatar else None
                }
                for user in users
            ]
            cache.set('dashboard_top_users', top_users, 60 * 10)
        return standard_response(data=top_users)
