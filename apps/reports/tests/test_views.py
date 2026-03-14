import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User
from apps.institutions.models import Institution
from apps.reports.models import Report

@pytest.fixture
def api_user(db):
    return User.objects.create_user(username="test@ex.uz", email="test@ex.uz", password="pass")

@pytest.fixture
def institution(db):
    return Institution.objects.create(
        external_id="ext-1", name="Sch-1", type="school",
        region="Tash", district="Yun", latitude=41.3, longitude=69.2
    )

@pytest.mark.django_db
class TestReportViews:
    def test_submit_report_unauthorized(self, client, institution):
        url = reverse('report-list-create')
        data = {
            "institution": institution.id,
            "comment": "Test"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_submit_report_success(self, client, api_user, institution):
        client.force_authenticate(user=api_user)
        url = reverse('report-list-create')
        # We need a dummy photo for testing
        from django.core.files.uploadedfile import SimpleUploadedFile
        photo = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        
        data = {
            "institution": institution.id,
            "comment": "Test report",
            "photo": photo
        }
        response = client.post(url, data, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
        assert Report.objects.count() == 1
