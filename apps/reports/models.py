from django.db import models
from django.utils.translation import gettext_lazy as _
from core.mixins import TimeStampedModel
from apps.users.models import User
from apps.institutions.models import Institution
from apps.promises.models import Promise
from core.utils import get_upload_path

class Report(TimeStampedModel):
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'
    RESOLVED = 'resolved'

    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (VERIFIED, _('Verified')),
        (REJECTED, _('Rejected')),
        (RESOLVED, _('Resolved')),
    ]

    FULFILLED = 'fulfilled'
    UNFULFILLED = 'unfulfilled'

    PROMISE_STATUS_CHOICES = [
        (FULFILLED, _('Fulfilled')),
        (UNFULFILLED, _('Unfulfilled')),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    promise = models.ForeignKey(Promise, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    promise_status = models.CharField(max_length=20, choices=PROMISE_STATUS_CHOICES, null=True, blank=True)
    photo = models.ImageField(upload_to=get_upload_path)
    comment = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    verification_count = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['institution', 'status']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Report by {self.user.email} on {self.institution.name}"

class ReportVerification(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='verifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_verifications')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('report', 'user')]

    def __str__(self):
        return f"Verification by {self.user.email} for {self.report.id}"
