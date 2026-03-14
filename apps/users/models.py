from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    CITIZEN = 'citizen'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (CITIZEN, _('Citizen')),
        (MODERATOR, _('Moderator')),
        (ADMIN, _('Admin')),
    ]

    NEW_USER = 'new_user'
    ACTIVE_INSPECTOR = 'active_inspector'
    TRUSTED_INSPECTOR = 'trusted_inspector'

    LEVEL_CHOICES = [
        (NEW_USER, _('New User')),
        (ACTIVE_INSPECTOR, _('Active Inspector')),
        (TRUSTED_INSPECTOR, _('Trusted Inspector')),
    ]

    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(max_length=13, unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CITIZEN)
    score = models.IntegerField(default=0)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default=NEW_USER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['score']),
            models.Index(fields=['level']),
        ]

    def __str__(self):
        return self.email

class ReputationLog(models.Model):
    REPORT_ACCEPTED = 'report_accepted'
    REPORT_REJECTED = 'report_rejected'
    REPORT_VERIFIED = 'report_verified'

    ACTION_CHOICES = [
        (REPORT_ACCEPTED, _('Report Accepted')),
        (REPORT_REJECTED, _('Report Rejected')),
        (REPORT_VERIFIED, _('Report Verified')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reputation_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} ({self.points})"
