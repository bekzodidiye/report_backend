from django.db.models import F
from apps.users.models import User, ReputationLog

class ReputationService:
    LEVELS = [
        (0, 49, User.NEW_USER),
        (50, 199, User.ACTIVE_INSPECTOR),
        (200, 999999, User.TRUSTED_INSPECTOR),
    ]

    @staticmethod
    def add_points(user, action, points):
        """
        Add/remove points, log the action, and check for level upgrades.
        """
        # Update user score using F() to avoid race conditions
        User.objects.filter(id=user.id).update(
            score=F('score') + points
        )
        
        # Log the reputation change
        ReputationLog.objects.create(
            user=user,
            action=action,
            points=points
        )
        
        # Reload user to check for level up
        user.refresh_from_db()
        ReputationService.update_level(user)

    @staticmethod
    def update_level(user):
        """
        Update user level based on their current score.
        """
        for min_score, max_score, level in ReputationService.LEVELS:
            if min_score <= user.score <= max_score:
                if user.level != level:
                    User.objects.filter(id=user.id).update(level=level)
                break
