"""
apps/construction/views.py
==========================
Construction Reports — barcha View'lar.
Mavjud Report, Problem view'lariga HECH QANDAY o'zgartirish kiritilmagan.
"""

import os
import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView

from core.responses import standard_response
from core.pagination import StandardPagination

from .models import ConstructionReport
from .serializers import (
    ConstructionReportCreateSerializer,
    ConstructionReportListSerializer,
    ConstructionReportDetailSerializer,
    ConstructionStatusUpdateSerializer,
)
from .services import ConstructionReportService

logger = logging.getLogger(__name__)

# ─── MODERATOR KEY ──────────────────────────────────────────────────────────────

def _check_moderator_key(request) -> bool:
    """X-Moderator-Key header == MODERATOR_SECRET env variable."""
    secret = os.getenv("MODERATOR_SECRET", "")
    provided = request.headers.get("X-Moderator-Key", "")
    return bool(secret and provided == secret)


# ─── RATE LIMIT HELPER ─────────────────────────────────────────────────────────

def _get_client_ip(request) -> str:
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _check_post_rate_limit(ip: str) -> bool:
    """2 POST / daqiqa per IP chegaralash. True → limit oshdi."""
    from django.core.cache import cache
    key = f"ratelimit:construction:{ip}"
    count = cache.get(key, 0)
    if count >= 2:
        return True
    cache.set(key, count + 1, 60)   # 60 soniya TTL
    return False


# ════════════════════════════════════════════════════════════════════════════════
class ConstructionReportListCreateView(APIView):
    """
    GET  /api/construction/reports  — Ro'yxat (filtrlar bilan)
    POST /api/construction/reports  — Yangi hisobot yuborish
    """

    permission_classes = [AllowAny]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    # ─── GET ────────────────────────────────────────────────────────────────────
    @swagger_auto_schema(
        operation_summary="Construction hisobotlari ro'yxati",
        operation_description=(
            "Barcha aktiv (o'chirilmagan) construction hisobotlarini qaytaradi. "
            "Filtrlar: status, severity, region, institution_id, sort_by."
        ),
        manual_parameters=[
            openapi.Parameter("status",         openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=["PENDING", "APPROVED", "REJECTED", "RESOLVED"]),
            openapi.Parameter("severity",       openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=["LOW", "MEDIUM", "HIGH"]),
            openapi.Parameter("region",         openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter("institution_id", openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("sort_by",        openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              enum=["created_at", "like_count", "view_count"]),
            openapi.Parameter("page",           openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter("page_size",      openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ],
        tags=["Construction Reports"],
        responses={200: openapi.Response("Paginated list")},
    )
    def get(self, request):
        filters = {
            "status":         request.query_params.get("status"),
            "severity":       request.query_params.get("severity"),
            "region":         request.query_params.get("region"),
            "institution_id": request.query_params.get("institution_id"),
            "sort_by":        request.query_params.get("sort_by", "created_at"),
        }
        try:
            page      = int(request.query_params.get("page", 1))
            page_size = int(request.query_params.get("page_size", 20))
        except (ValueError, TypeError):
            page, page_size = 1, 20

        result = ConstructionReportService.get_list(filters, page, page_size)
        return standard_response(data=result)

    # ─── POST ───────────────────────────────────────────────────────────────────
    @swagger_auto_schema(
        operation_summary="Yangi construction hisoboti yuborish",
        operation_description=(
            "**Content-Type:** multipart/form-data\n\n"
            "Majburiy: title, description, severity, latitude, longitude.\n"
            "Ixtiyoriy: image (jpg/png, max 5MB), user_id (UUID), institution."
        ),
        request_body=ConstructionReportCreateSerializer,
        tags=["Construction Reports"],
        responses={
            201: openapi.Response("Yaratildi"),
            400: openapi.Response("Validatsiya xatosi"),
            429: openapi.Response("Juda ko'p so'rov (2/daqiqa)"),
        },
    )
    def post(self, request):
        ip = _get_client_ip(request)

        if _check_post_rate_limit(ip):
            return standard_response(
                success=False,
                message="Rate limit exceeded: maksimum 2 ta so'rov/daqiqa.",
                status=429,
            )

        serializer = ConstructionReportCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(success=False, errors=serializer.errors, status=400)

        image_file = serializer.validated_data.pop("image", None)

        try:
            report = ConstructionReportService.create(
                validated_data=serializer.validated_data,
                image_file=image_file,
            )
            return standard_response(
                data=ConstructionReportDetailSerializer(report).data,
                message="Hisobot muvaffaqiyatli yuborildi.",
                status=201,
            )
        except Exception as exc:
            logger.error("ConstructionReport create error: %s", exc)
            return standard_response(success=False, message=str(exc), status=500)


# ════════════════════════════════════════════════════════════════════════════════
class ConstructionReportDetailView(APIView):
    """
    GET    /api/construction/reports/{id}  — Batafsil ma'lumot
    DELETE /api/construction/reports/{id}  — Soft delete (moderator only)
    """

    permission_classes = [AllowAny]

    # ─── GET ────────────────────────────────────────────────────────────────────
    @swagger_auto_schema(
        operation_summary="Construction hisoboti batafsil",
        tags=["Construction Reports"],
        responses={
            200: openapi.Response("Batafsil ma'lumot"),
            404: openapi.Response("Topilmadi"),
        },
    )
    def get(self, request, pk):
        data = ConstructionReportService.get_detail(str(pk))
        if data is None:
            return standard_response(
                success=False, message="Hisobot topilmadi.", status=404
            )
        return standard_response(data=data)

    # ─── DELETE ─────────────────────────────────────────────────────────────────
    @swagger_auto_schema(
        operation_summary="Construction hisobotini o'chirish (soft delete)",
        operation_description="Faqat moderatorlar uchun. X-Moderator-Key header talab etiladi.",
        manual_parameters=[
            openapi.Parameter(
                "X-Moderator-Key", openapi.IN_HEADER,
                type=openapi.TYPE_STRING, required=True,
            )
        ],
        tags=["Construction Reports"],
        responses={
            200: openapi.Response("Muvaffaqiyatli o'chirildi"),
            403: openapi.Response("Ruxsat berilmagan"),
            404: openapi.Response("Topilmadi"),
        },
    )
    def delete(self, request, pk):
        if not _check_moderator_key(request):
            return standard_response(success=False, message="Ruxsat berilmagan.", status=403)

        deleted = ConstructionReportService.soft_delete(str(pk))
        if not deleted:
            return standard_response(success=False, message="Hisobot topilmadi.", status=404)
        return standard_response(message="Muvaffaqiyatli o'chirildi.")


# ════════════════════════════════════════════════════════════════════════════════
class ConstructionReportStatusView(APIView):
    """
    PATCH /api/construction/reports/{id}/status — Statusni yangilash (moderator)
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Construction hisoboti statusini yangilash",
        operation_description="Faqat moderatorlar uchun. X-Moderator-Key header talab etiladi.",
        request_body=ConstructionStatusUpdateSerializer,
        manual_parameters=[
            openapi.Parameter(
                "X-Moderator-Key", openapi.IN_HEADER,
                type=openapi.TYPE_STRING, required=True,
            )
        ],
        tags=["Construction Reports"],
        responses={
            200: openapi.Response("Status yangilandi"),
            400: openapi.Response("Validatsiya xatosi"),
            403: openapi.Response("Ruxsat berilmagan"),
            404: openapi.Response("Topilmadi"),
        },
    )
    def patch(self, request, pk):
        if not _check_moderator_key(request):
            return standard_response(success=False, message="Ruxsat berilmagan.", status=403)

        serializer = ConstructionStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(success=False, errors=serializer.errors, status=400)

        data = ConstructionReportService.update_status(
            report_id=str(pk),
            new_status=serializer.validated_data["status"],
        )
        if data is None:
            return standard_response(success=False, message="Hisobot topilmadi.", status=404)
        return standard_response(data=data, message="Status muvaffaqiyatli yangilandi.")


# ════════════════════════════════════════════════════════════════════════════════
class ConstructionReportLikeView(APIView):
    """
    POST /api/construction/reports/{id}/like — Hisobotni yoqtirish
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Construction hisobotini yoqtirish",
        operation_description=(
            "Bir IP manzilidan faqat bir marta like bosish mumkin. "
            "Takroriy like 409 Conflict qaytaradi."
        ),
        tags=["Construction Reports"],
        responses={
            200: openapi.Response("Like qo'shildi"),
            404: openapi.Response("Topilmadi"),
            409: openapi.Response("Allaqachon yoqtirgan"),
        },
    )
    def post(self, request, pk):
        ip = _get_client_ip(request)
        like_count, error = ConstructionReportService.like(str(pk), ip)

        if error == "not_found":
            return standard_response(success=False, message="Hisobot topilmadi.", status=404)
        if error == "already_liked":
            return standard_response(
                success=False,
                message="Siz bu hisobotni allaqachon yoqtirgan edingiz.",
                status=409,
            )

        return standard_response(data={"like_count": like_count})
