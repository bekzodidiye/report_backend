"""
ConstructionReportService
=========================
Barcha biznes-mantiq shu joyda. View-lar faqat HTTP
qatlami bilan shug'ullanadi, service — ma'lumotlar bilan.
"""

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone

import requests
from django.core.cache import cache
from django.utils.timezone import now

from .models import ConstructionReport
from .serializers import (
    ConstructionReportDetailSerializer,
    ConstructionReportListSerializer,
)

logger = logging.getLogger(__name__)

# ─── CACHE KEY HELPERS ──────────────────────────────────────────────────────────

def _list_cache_key(params: dict) -> str:
    raw = json.dumps(params, sort_keys=True)
    h = hashlib.md5(raw.encode()).hexdigest()
    return f"construction:list:{h}"

def _detail_cache_key(report_id: str) -> str:
    return f"construction:detail:{report_id}"

def _like_cache_key(ip: str, report_id: str) -> str:
    return f"construction:like:{ip}:{report_id}"

# ─── GEOCODING ──────────────────────────────────────────────────────────────────

def _reverse_geocode(lat: float, lng: float) -> str | None:
    """
    Nominatim reverse geocoding, 24 soat keshlanadi.
    """
    geo_key = f"construction:geo:{lat:.4f}:{lng:.4f}"
    cached = cache.get(geo_key)
    if cached:
        return cached

    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lng, "format": "json"}
        headers = {"User-Agent": "CivicPlatform/1.0"}
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            address = data.get("display_name")
            cache.set(geo_key, address, 86400)   # 24 soat
            return address
    except Exception as exc:
        logger.warning("Geocoding failed for (%s,%s): %s", lat, lng, exc)
    return None


# ════════════════════════════════════════════════════════════════════════════════
class ConstructionReportService:
    """
    Barcha CRUD + kesh + geocoding operatsiyalari.
    """

    # ─── LIST ───────────────────────────────────────────────────────────────────
    @staticmethod
    def get_list(filters: dict, page: int, page_size: int) -> dict:
        """
        Filtrlar: category (institution), status, severity, region, sort_by.
        Redis kesh: 3 daqiqa.
        """
        page_size = min(page_size, 100)
        cache_params = {**filters, "page": page, "page_size": page_size}
        cache_key = _list_cache_key(cache_params)

        cached = cache.get(cache_key)
        if cached:
            return cached

        qs = ConstructionReport.objects.filter(deleted_at__isnull=True)

        if filters.get("status"):
            qs = qs.filter(status=filters["status"])
        if filters.get("severity"):
            qs = qs.filter(severity=filters["severity"])
        if filters.get("region"):
            qs = qs.filter(address_name__icontains=filters["region"])
        if filters.get("institution_id"):
            qs = qs.filter(institution_id=filters["institution_id"])

        sort_map = {
            "like_count": "-like_count",
            "view_count": "-view_count",
            "created_at": "-created_at",
        }
        qs = qs.order_by(sort_map.get(filters.get("sort_by"), "-created_at"))

        total = qs.count()
        offset = (page - 1) * page_size
        items = qs[offset: offset + page_size]

        result = {
            "items": ConstructionReportListSerializer(items, many=True).data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }

        cache.set(cache_key, result, 180)   # 3 daqiqa
        return result

    # ─── DETAIL ─────────────────────────────────────────────────────────────────
    @staticmethod
    def get_detail(report_id: str):
        """
        Redis kesh: 5 daqiqa.
        Ko'rish sonini Celery vazifasi orqali oshiradi (async).
        """
        cache_key = _detail_cache_key(report_id)
        cached = cache.get(cache_key)
        if cached:
            # view_count'ni asinxron oshirish
            try:
                from apps.construction.tasks import increment_construction_view_count
                increment_construction_view_count.delay(report_id)
            except Exception:
                pass
            return cached

        try:
            report = ConstructionReport.objects.select_related("institution").get(
                pk=report_id, deleted_at__isnull=True
            )
        except (ConstructionReport.DoesNotExist, Exception):
            return None

        data = ConstructionReportDetailSerializer(report).data
        cache.set(cache_key, data, 300)   # 5 daqiqa

        try:
            from apps.construction.tasks import increment_construction_view_count
            increment_construction_view_count.delay(report_id)
        except Exception:
            pass

        return data

    # ─── CREATE ─────────────────────────────────────────────────────────────────
    @staticmethod
    def create(validated_data: dict, image_file=None) -> ConstructionReport:
        """
        1 → Geocoding
        2 → Rasm yuklash (S3 yoki lokal)
        3 → Saqlash
        4 → Keshni tozalash
        5 → Telegram xabari (Celery)
        """
        image_url = None
        thumbnail_url = None

        if image_file:
            image_url, thumbnail_url = ConstructionReportService._handle_image(image_file)

        lat = validated_data.get("latitude")
        lng = validated_data.get("longitude")
        address_name = _reverse_geocode(lat, lng)

        report = ConstructionReport.objects.create(
            title=validated_data["title"],
            description=validated_data["description"],
            institution=validated_data.get("institution"),
            severity=validated_data["severity"],
            latitude=lat,
            longitude=lng,
            address_name=address_name,
            user_id=validated_data.get("user_id"),
            image_url=image_url,
            thumbnail_url=thumbnail_url,
        )

        # Keshni tozalash
        ConstructionReportService._invalidate_list_cache()

        # Telegram
        try:
            from apps.construction.tasks import notify_telegram_construction
            notify_telegram_construction.delay(str(report.id))
        except Exception as exc:
            logger.warning("Telegram task failed: %s", exc)

        return report

    # ─── UPDATE STATUS ──────────────────────────────────────────────────────────
    @staticmethod
    def update_status(report_id: str, new_status: str):
        try:
            report = ConstructionReport.objects.get(pk=report_id, deleted_at__isnull=True)
        except ConstructionReport.DoesNotExist:
            return None

        report.status = new_status
        report.save(update_fields=["status", "updated_at"])

        cache.delete(_detail_cache_key(report_id))
        ConstructionReportService._invalidate_list_cache()

        if new_status == ConstructionReport.RESOLVED:
            try:
                from apps.construction.tasks import notify_telegram_construction_resolved
                notify_telegram_construction_resolved.delay(report_id)
            except Exception as exc:
                logger.warning("Resolved telegram task failed: %s", exc)

        return ConstructionReportDetailSerializer(report).data

    # ─── LIKE ───────────────────────────────────────────────────────────────────
    @staticmethod
    def like(report_id: str, ip: str):
        """
        1 like per IP per hisobot.
        Redis'da doimiy kalit, DB'da minutlik sinxronizatsiya.
        """
        like_key = _like_cache_key(ip, report_id)
        if cache.get(like_key):
            return None, "already_liked"

        # Hisobot mavjudligini tekshirish
        try:
            report = ConstructionReport.objects.get(pk=report_id, deleted_at__isnull=True)
        except ConstructionReport.DoesNotExist:
            return None, "not_found"

        # Doimiy belgi qo'yish
        cache.set(like_key, "1", None)   # timeout=None → permanent

        # DB'da atomik oshirish
        ConstructionReport.objects.filter(pk=report_id).update(
            like_count=models_F("like_count") + 1
        )
        report.refresh_from_db(fields=["like_count"])
        return report.like_count, None

    # ─── SOFT DELETE ────────────────────────────────────────────────────────────
    @staticmethod
    def soft_delete(report_id: str) -> bool:
        updated = ConstructionReport.objects.filter(
            pk=report_id, deleted_at__isnull=True
        ).update(deleted_at=now())

        if updated:
            cache.delete(_detail_cache_key(report_id))
            ConstructionReportService._invalidate_list_cache()
            return True
        return False

    # ─── HELPERS ────────────────────────────────────────────────────────────────
    @staticmethod
    def _handle_image(image_file) -> tuple[str | None, str | None]:
        """
        USE_S3=True → S3/R2'ga yuklash.
        USE_S3=False → Lokal media/ katalogiga saqlash.
        URLlarni qaytaradi: (image_url, thumbnail_url)
        """
        try:
            from django.conf import settings
            from django.core.files.storage import default_storage

            ext = image_file.name.rsplit(".", 1)[-1].lower()
            filename = f"construction/{uuid.uuid4()}.{ext}"
            saved_path = default_storage.save(filename, image_file)
            image_url = default_storage.url(saved_path)

            # Sodda thumbnail: ayni fayl, _thumb qo'shimchasi bilan
            thumb_filename = f"construction/{uuid.uuid4()}_thumb.{ext}"
            # Real loyihada Pillow bilan o'lchamni qisqartirish kerak
            image_file.seek(0)
            thumb_path = default_storage.save(thumb_filename, image_file)
            thumbnail_url = default_storage.url(thumb_path)

            return image_url, thumbnail_url
        except Exception as exc:
            logger.error("Image upload failed: %s", exc)
            return None, None

    @staticmethod
    def _invalidate_list_cache():
        """Barcha list kesh kalitlarini tozalash."""
        try:
            cache.delete_pattern("construction:list:*")
        except Exception:
            # delete_pattern Django standart cache-da yo'q bo'lishi mumkin
            pass


# F() ifodasi import (aynan kerakli joyda)
from django.db.models import F as models_F   # noqa: E402
