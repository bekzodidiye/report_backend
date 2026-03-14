"""
tests/test_construction_reports.py
===================================
Construction Reports uchun barcha unit testlar.
Mavjud test fayllari o'ZGARTIRILMAGAN.
"""

import uuid
import pytest
from django.test import override_settings
from rest_framework.test import APIClient

MODERATOR_KEY = "test-secret-key"
BASE_URL = "/api/v1/construction/reports/"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def institution(db):
    from apps.institutions.models import Institution
    return Institution.objects.create(
        external_id="TEST-001",
        name="Test Maktab",
        type="school",
        region="Toshkent",
        district="Yunusobod",
        latitude=41.311,
        longitude=69.279,
    )


@pytest.fixture
def construction_report(db, institution):
    from apps.construction.models import ConstructionReport
    return ConstructionReport.objects.create(
        title="Test Qurilish Hisoboti",
        description="Test tavsifi — minimal 10 ta belgi.",
        institution=institution,
        severity=ConstructionReport.HIGH,
        latitude=41.311,
        longitude=69.279,
        address_name="Toshkent shahar",
    )


# ──────────────────────────────────────────────────────────────────
# GET /api/construction/reports/
# ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_list_returns_200(client, construction_report):
    """Ro'yxat muvaffaqiyatli qaytishi kerak."""
    resp = client.get(BASE_URL)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "items" in data["data"]


@pytest.mark.django_db
def test_list_filtered_by_status(client, construction_report):
    """Status filtri ishlashi kerak."""
    resp = client.get(BASE_URL, {"status": "PENDING"})
    assert resp.status_code == 200
    for item in resp.json()["data"]["items"]:
        assert item["status"] == "PENDING"


@pytest.mark.django_db
def test_list_filtered_by_severity(client, construction_report):
    """Severity filtri ishlashi kerak."""
    resp = client.get(BASE_URL, {"severity": "HIGH"})
    assert resp.status_code == 200


@pytest.mark.django_db
def test_list_filtered_by_category(client, construction_report):
    """Institution_id filtri ishlashi kerak."""
    resp = client.get(BASE_URL, {"institution_id": construction_report.institution_id})
    assert resp.status_code == 200


# ──────────────────────────────────────────────────────────────────
# GET /api/construction/reports/{id}/
# ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_detail_returns_200(client, construction_report):
    """Mavjud hisobot batafsil qaytishi kerak."""
    resp = client.get(f"{BASE_URL}{construction_report.id}/")
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "Test Qurilish Hisoboti"


@pytest.mark.django_db
def test_detail_nonexistent_returns_404(client):
    """Mavjud bo'magan ID uchun 404 qaytishi kerak."""
    resp = client.get(f"{BASE_URL}{uuid.uuid4()}/")
    assert resp.status_code == 404
    assert resp.json()["success"] is False


# ──────────────────────────────────────────────────────────────────
# POST /api/construction/reports/
# ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_create_valid_report(client, institution):
    """To'g'ri ma'lumotlar bilan 201 qaytishi kerak."""
    resp = client.post(BASE_URL, {
        "title":       "Yangi qurilish xabari",
        "description": "Bu 10 ta belgidan uzun tavsif.",
        "institution": institution.id,
        "severity":    "MEDIUM",
        "latitude":    "41.311",
        "longitude":   "69.279",
    }, format="multipart")
    assert resp.status_code == 201
    assert resp.json()["success"] is True


@pytest.mark.django_db
def test_create_missing_title_returns_400(client, institution):
    """Title bo'lmasa 400 qaytishi kerak."""
    resp = client.post(BASE_URL, {
        "description": "Bu malumot.",
        "severity":    "LOW",
        "latitude":    "41.311",
        "longitude":   "69.279",
    }, format="multipart")
    assert resp.status_code == 400
    assert "title" in resp.json()["errors"]


@pytest.mark.django_db
def test_create_invalid_severity_returns_400(client, institution):
    """Noto'g'ri severity qiymati 400 qaytishi kerak."""
    resp = client.post(BASE_URL, {
        "title":       "Test",
        "description": "Description uzun bo'lishi kerak.",
        "severity":    "EXTREME",
        "latitude":    "41.311",
        "longitude":   "69.279",
    }, format="multipart")
    assert resp.status_code == 400
    assert "severity" in resp.json()["errors"]


@pytest.mark.django_db
def test_create_invalid_coordinates_returns_400(client):
    """Noto'g'ri koordinatlar 400 qaytishi kerak."""
    resp = client.post(BASE_URL, {
        "title":       "Joylashuv xatosi",
        "description": "Bu tavsif etarlicha uzun.",
        "severity":    "LOW",
        "latitude":    "999",
        "longitude":   "69.279",
    }, format="multipart")
    assert resp.status_code == 400
    assert "latitude" in resp.json()["errors"]


@pytest.mark.django_db
@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
def test_create_rate_limit_exceeded(client, institution):
    """2 dan ortiq so'rov 429 qaytishi kerak."""
    data = {
        "title":       "Rate limit test",
        "description": "Bu tavsif 10 belgidan uzun.",
        "severity":    "LOW",
        "latitude":    "41.311",
        "longitude":   "69.279",
    }
    client.post(BASE_URL, data, format="multipart", REMOTE_ADDR="10.0.0.1")
    client.post(BASE_URL, data, format="multipart", REMOTE_ADDR="10.0.0.1")
    resp = client.post(BASE_URL, data, format="multipart", REMOTE_ADDR="10.0.0.1")
    assert resp.status_code == 429


# ──────────────────────────────────────────────────────────────────
# PATCH /api/construction/reports/{id}/status/
# ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
@override_settings(MODERATOR_SECRET="")
def test_patch_status_without_key_returns_403(client, construction_report):
    """Moderator key bo'lmasa 403 qaytishi kerak."""
    resp = client.patch(
        f"{BASE_URL}{construction_report.id}/status/",
        {"status": "APPROVED"}, format="json",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
@override_settings(MODERATOR_SECRET=MODERATOR_KEY)
def test_patch_status_with_valid_key_returns_200(client, construction_report):
    """To'g'ri key bilan 200 qaytishi kerak."""
    resp = client.patch(
        f"{BASE_URL}{construction_report.id}/status/",
        {"status": "APPROVED"}, format="json",
        HTTP_X_MODERATOR_KEY=MODERATOR_KEY,
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "APPROVED"


# ──────────────────────────────────────────────────────────────────
# POST /api/construction/reports/{id}/like/
# ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
def test_like_returns_200(client, construction_report):
    """Like bosish 200 qaytishi kerak."""
    resp = client.post(
        f"{BASE_URL}{construction_report.id}/like/",
        REMOTE_ADDR="10.1.1.1",
    )
    assert resp.status_code == 200
    assert "like_count" in resp.json()["data"]


@pytest.mark.django_db
@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
def test_like_duplicate_returns_409(client, construction_report):
    """Bir IP ikkinchi marta like bossa 409 qaytishi kerak."""
    client.post(f"{BASE_URL}{construction_report.id}/like/", REMOTE_ADDR="10.1.1.2")
    resp = client.post(f"{BASE_URL}{construction_report.id}/like/", REMOTE_ADDR="10.1.1.2")
    assert resp.status_code == 409


# ──────────────────────────────────────────────────────────────────
# DELETE /api/construction/reports/{id}/
# ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
@override_settings(MODERATOR_SECRET="")
def test_delete_without_key_returns_403(client, construction_report):
    """Key bo'lmasa 403 qaytishi kerak."""
    resp = client.delete(f"{BASE_URL}{construction_report.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
@override_settings(MODERATOR_SECRET=MODERATOR_KEY)
def test_delete_with_valid_key_returns_200(client, construction_report):
    """To'g'ri key bilan 200 qaytishi kerak."""
    resp = client.delete(
        f"{BASE_URL}{construction_report.id}/",
        HTTP_X_MODERATOR_KEY=MODERATOR_KEY,
    )
    assert resp.status_code == 200


@pytest.mark.django_db
@override_settings(MODERATOR_SECRET=MODERATOR_KEY)
def test_deleted_report_returns_404(client, construction_report):
    """O'chirilgan hisobotni GET qilganda 404 qaytishi kerak."""
    client.delete(
        f"{BASE_URL}{construction_report.id}/",
        HTTP_X_MODERATOR_KEY=MODERATOR_KEY,
    )
    resp = client.get(f"{BASE_URL}{construction_report.id}/")
    assert resp.status_code == 404
