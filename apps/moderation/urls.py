from django.urls import path
from .views import PendingReportsView, ModerateReportView, PendingProblemsView

urlpatterns = [
    path('reports/', PendingReportsView.as_view(), name='moderation-reports'),
    path('reports/<int:id>/', ModerateReportView.as_view(), name='moderate-report'),
    path('problems/', PendingProblemsView.as_view(), name='moderation-problems'),
]
