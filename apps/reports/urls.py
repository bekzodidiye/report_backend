from django.urls import path
from .views import ReportCreateListView, ReportVerifyView

urlpatterns = [
    path('', ReportCreateListView.as_view(), name='report-list-create'),
    path('<int:id>/verify/', ReportVerifyView.as_view(), name='report-verify'),
]
