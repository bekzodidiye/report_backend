from django.urls import path
from .views import (
    ConstructionReportListCreateView,
    ConstructionReportDetailView,
    ConstructionReportStatusView,
    ConstructionReportLikeView,
)

urlpatterns = [
    # GET  /api/construction/reports/       → ro'yxat + filtrlar
    # POST /api/construction/reports/       → yangi hisobot
    path("reports/",                   ConstructionReportListCreateView.as_view(), name="construction-list-create"),

    # GET    /api/construction/reports/{pk}/ → batafsil
    # DELETE /api/construction/reports/{pk}/ → soft delete
    path("reports/<uuid:pk>/",         ConstructionReportDetailView.as_view(),      name="construction-detail"),

    # PATCH /api/construction/reports/{pk}/status/ → status yangilash
    path("reports/<uuid:pk>/status/",  ConstructionReportStatusView.as_view(),      name="construction-status"),

    # POST /api/construction/reports/{pk}/like/ → like bosish
    path("reports/<uuid:pk>/like/",    ConstructionReportLikeView.as_view(),        name="construction-like"),
]
