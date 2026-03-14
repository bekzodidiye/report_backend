"""
apps/construction/tasks.py
==========================
Yangi Celery vazifalari — faqat Construction moduliga tegishli.
Mavjud tasks.py fayllariga HECH QANDAY o'zgartirish kiritilmagan.
"""

import logging
import os

from celery import shared_task
from django.core.cache import cache

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────
@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def notify_telegram_construction(self, report_id: str):
    """
    Yangi qurilish hisoboti kelganda moderatorga Telegram xabari yuboradi.

    Format:
        🏗️ Yangi qurilish shikoyati!
        📍 Manzil: {address_name}
        ⚠️ Darajasi: {severity}
        📝 {title}
        🔗 /api/construction/reports/{id}
    """
    try:
        from apps.construction.models import ConstructionReport

        report = ConstructionReport.objects.select_related("institution").get(pk=report_id)

        category_name = report.institution.name if report.institution else "Noma'lum"
        address = report.address_name or f"{report.latitude}, {report.longitude}"

        severity_emoji = {"LOW": "🟡", "MEDIUM": "🟠", "HIGH": "🔴"}.get(report.severity, "⚠️")

        text = (
            f"🏗️ <b>Yangi qurilish shikoyati!</b>\n\n"
            f"📍 <b>Manzil:</b> {address}\n"
            f"📂 <b>Muassasa:</b> {category_name}\n"
            f"{severity_emoji} <b>Darajasi:</b> {report.severity}\n"
            f"📝 <b>Sarlavha:</b> {report.title}\n\n"
            f"🔗 /api/construction/reports/{report.id}"
        )

        _send_telegram(
            chat_id=os.getenv("TELEGRAM_MODERATOR_CHAT_ID"),
            text=text,
            image_url=report.image_url,
        )
        logger.info("Telegram notification sent for construction report %s", report_id)

    except ConstructionReport.DoesNotExist:
        logger.warning("Construction report %s not found for Telegram notification", report_id)
    except Exception as exc:
        logger.error("Telegram notification failed for %s: %s", report_id, exc)
        raise self.retry(exc=exc)


# ──────────────────────────────────────────────────────────────────
@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def notify_telegram_construction_resolved(self, report_id: str):
    """
    Muammo hal bo'lganda ommaviy kanalga xabar yuboradi.

    Format:
        ✅ Qurilish muammosi hal etildi!
        📍 {address_name}
        📝 {title}
    """
    try:
        from apps.construction.models import ConstructionReport

        report = ConstructionReport.objects.get(pk=report_id)
        address = report.address_name or f"{report.latitude}, {report.longitude}"

        text = (
            f"✅ <b>Qurilish muammosi hal etildi!</b>\n\n"
            f"📍 <b>Manzil:</b> {address}\n"
            f"📝 <b>Sarlavha:</b> {report.title}"
        )

        _send_telegram(
            chat_id=os.getenv("TELEGRAM_PUBLIC_CHANNEL_ID"),
            text=text,
        )
        logger.info("Resolved Telegram notification sent for %s", report_id)

    except ConstructionReport.DoesNotExist:
        logger.warning("Report %s not found for RESOLVED notification", report_id)
    except Exception as exc:
        logger.error("Resolved Telegram notification failed for %s: %s", report_id, exc)
        raise self.retry(exc=exc)


# ──────────────────────────────────────────────────────────────────
@shared_task
def increment_construction_view_count(report_id: str):
    """
    Ko'rish sonini DB'da oshiradi.
    Redis'dan pending view'larni sinxronlashtiradi.
    """
    try:
        from apps.construction.models import ConstructionReport
        from django.db.models import F

        ConstructionReport.objects.filter(
            pk=report_id, deleted_at__isnull=True
        ).update(view_count=F("view_count") + 1)

        logger.debug("View count incremented for construction report %s", report_id)

    except Exception as exc:
        logger.error("increment_construction_view_count failed for %s: %s", report_id, exc)


# ──────────────────────────────────────────────────────────────────
@shared_task
def sync_construction_like_counts():
    """
    Celery Beat har 60 soniyada chaqiradi.
    Redis'dagi kutilayotgan like'larni DB'ga sinxronlashtiradi.
    (Joriy arxitekturada like'lar to'g'ridan-to'g'ri DB'ga yoziladi,
    ammo kelajakda Redis buffer uchun bu joyda kengaytirish mumkin.)
    """
    logger.debug("sync_construction_like_counts: running periodic sync check")


# ──────────────────────────────────────────────────────────────────
def _send_telegram(chat_id: str | None, text: str, image_url: str | None = None):
    """
    Telegram Bot API orqali xabar yuboradi.
    TELEGRAM_BOT_TOKEN muhit o'zgaruvchisi kerak.
    """
    import requests as req_lib

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token or not chat_id:
        logger.warning("Telegram not configured (TELEGRAM_BOT_TOKEN or chat_id missing)")
        return

    base_url = f"https://api.telegram.org/bot{bot_token}"

    if image_url:
        req_lib.post(
            f"{base_url}/sendPhoto",
            data={"chat_id": chat_id, "caption": text, "parse_mode": "HTML", "photo": image_url},
            timeout=10,
        )
    else:
        req_lib.post(
            f"{base_url}/sendMessage",
            data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10,
        )
