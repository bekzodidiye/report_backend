from django.db.models import Count
from apps.institutions.models import Institution
from apps.reports.models import Report
from apps.problems.models import Problem
from apps.users.models import User

class DashboardService:
    @staticmethod
    def get_stats():
        return {
            "total_institutions": Institution.objects.count(),
            "total_reports": Report.objects.count(),
            "verified_reports": Report.objects.filter(status='verified').count(),
            "total_problems": Problem.objects.count(),
            "verified_problems": Problem.objects.filter(status='verified').count(),
            "total_users": User.objects.count()
        }

    @staticmethod
    def get_map_markers():
        return Institution.objects.values('id', 'latitude', 'longitude', 'status', 'name')

    @staticmethod
    def get_top_users(limit=10):
        return User.objects.order_by('-score')[:limit]
