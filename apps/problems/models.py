from django.db import models
from django.utils.translation import gettext_lazy as _
from core.mixins import TimeStampedModel
from apps.users.models import User
from apps.institutions.models import Institution
from core.utils import get_upload_path

class Problem(TimeStampedModel):
    SANITATION = 'sanitation'
    WATER = 'water'
    ELECTRICITY = 'electricity'
    HEATING = 'heating'
    INTERNET = 'internet'
    FURNITURE = 'furniture'
    SAFETY = 'safety'
    OTHER = 'other'

    CATEGORY_CHOICES = [
        (SANITATION, _('Sanitation')),
        (WATER, _('Water')),
        (ELECTRICITY, _('Electricity')),
        (HEATING, _('Heating')),
        (INTERNET, _('Internet')),
        (FURNITURE, _('Furniture')),
        (SAFETY, _('Safety')),
        (OTHER, _('Other')),
    ]

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

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='problems')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='problems')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    photo = models.ImageField(upload_to=get_upload_path)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    verification_count = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['institution', 'status']),
            models.Index(fields=['category']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category} problem at {self.institution.name}"

class ProblemVerification(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='verifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='problem_verifications')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('problem', 'user')]

    def __str__(self):
        return f"Verification by {self.user.email} for problem {self.problem.id}"
