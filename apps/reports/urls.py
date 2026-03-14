from django.urls import path
from .views import ReportCreateListView, ReportVerifyView, ReportDetailView

urlpatterns = [
    path('',              ReportCreateListView.as_view(), name='report-list-create'),
    path('<int:id>/',     ReportDetailView.as_view(),     name='report-detail'),     # GET + DELETE
    path('<int:id>/verify/', ReportVerifyView.as_view(),  name='report-verify'),
]
