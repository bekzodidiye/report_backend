from django.db import models
from django.utils.translation import gettext_lazy as _
from core.mixins import TimeStampedModel
from apps.users.models import User
from apps.institutions.models import Institution

class Promise(TimeStampedModel):
    PENDING = 'pending'
    FULFILLED = 'fulfilled'
    UNFULFILLED = 'unfulfilled'

    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (FULFILLED, _('Fulfilled')),
        (UNFULFILLED, _('Unfulfilled')),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='promises')
    title = models.CharField(max_length=300)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    deadline = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_promises')

    class Meta:
        indexes = [
            models.Index(fields=['institution', 'status']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.institution.name}"
