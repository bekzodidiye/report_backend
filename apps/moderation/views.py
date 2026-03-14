from rest_framework import generics, permissions, status
from drf_yasg.utils import swagger_auto_schema
from core.responses import standard_response
from core.permissions import IsModerator
from core.pagination import StandardPagination
from apps.reports.models import Report
from apps.reports.serializers import ReportSerializer
from apps.reports.services import ReportService
from apps.problems.models import Problem
from apps.problems.serializers import ProblemSerializer

class PendingReportsView(generics.ListAPIView):
    queryset = Report.objects.filter(status='pending').order_by('-created_at')
    serializer_class = ReportSerializer
    permission_classes = [IsModerator]
    pagination_class = StandardPagination

    @swagger_auto_schema(tags=['moderation'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ModerateReportView(generics.UpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsModerator]
    lookup_field = 'id'

    @swagger_auto_schema(tags=['moderation'])
    def patch(self, request, *args, **kwargs):
        report_id = kwargs.get('id')
        action = request.data.get('status')
        
        if action == 'verified':
            # In a real scenario, moderation verification might be different from citizen verification
            # But here we follow logic: moderator can directly verify or reject
            report = self.get_object()
            report.status = 'verified'
            report.save()
            return standard_response(data=self.get_serializer(report).data)
        elif action == 'rejected':
            report = ReportService.reject_report(report_id, request.user)
            return standard_response(data=self.get_serializer(report).data)
        
        return standard_response(success=False, message="Invalid action", status=400)

class PendingProblemsView(generics.ListAPIView):
    queryset = Problem.objects.filter(status='pending').order_by('-created_at')
    serializer_class = ProblemSerializer
    permission_classes = [IsModerator]
    pagination_class = StandardPagination

    @swagger_auto_schema(tags=['moderation'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
