import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User

@pytest.mark.django_db
class TestUserViews:
    def test_register_success(self, client):
        url = reverse('register')
        data = {
            "email": "test@example.uz",
            "password": "password123",
            "phone": "+998901234567"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert User.objects.filter(email=data['email']).exists()

    def test_register_duplicate_email(self, client):
        User.objects.create_user(username="test@example.uz", email="test@example.uz", password="password")
        url = reverse('register')
        data = {
            "email": "test@example.uz",
            "password": "password123"
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False

    def test_me_protected_endpoint(self, client):
        url = reverse('me')
        response = client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
