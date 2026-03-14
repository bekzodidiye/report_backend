import pytest
from apps.users.services import ReputationService
from apps.users.models import User

@pytest.mark.django_db
def test_reputation_level_up():
    user = User.objects.create_user(username="test@ex.uz", email="test@ex.uz", password="pass")
    assert user.level == User.NEW_USER
    
    # Add points to reach active inspector
    ReputationService.add_points(user, 'report_verified', 60)
    user.refresh_from_db()
    assert user.score == 60
    assert user.level == User.ACTIVE_INSPECTOR

    # Add points to reach trusted inspector
    ReputationService.add_points(user, 'report_verified', 200)
    user.refresh_from_db()
    assert user.level == User.TRUSTED_INSPECTOR
