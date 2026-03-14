import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.institutions.models import Institution


class ConstructionReport(models.Model):
    """
    Qurilish/ta'mirlash bo'yicha fuqarolar hisobotlari.
    Mavjud Report modelidan to'liq ajratilgan — turli jadval, turli mantiq.
    """

    # ─── STATUS ────────────────────────────────────────────────────────────────
    PENDING  = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    RESOLVED = 'RESOLVED'

    STATUS_CHOICES = [
        (PENDING,  _('Pending')),
        (APPROVED, _('Approved')),
        (REJECTED, _('Rejected')),
        (RESOLVED, _('Resolved')),
    ]

    # ─── SEVERITY ───────────────────────────────────────────────────────────────
    LOW    = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH   = 'HIGH'

    SEVERITY_CHOICES = [
        (LOW,    _('Low')),
        (MEDIUM, _('Medium')),
        (HIGH,   _('High')),
    ]

    # ─── FIELDS ─────────────────────────────────────────────────────────────────
    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id       = models.UUIDField(null=True, blank=True, db_index=True,
                                     help_text=_('Anonymous if null'))

    title         = models.CharField(max_length=100)
    description   = models.TextField()
    institution   = models.ForeignKey(
                        Institution, on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='construction_reports'
                    )

    severity      = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    latitude      = models.FloatField()
    longitude     = models.FloatField()
    address_name  = models.CharField(max_length=500, null=True, blank=True,
                                     help_text=_('Auto-filled via reverse geocoding'))

    view_count    = models.PositiveIntegerField(default=0)
    like_count    = models.PositiveIntegerField(default=0)

    image_url     = models.URLField(max_length=2000, null=True, blank=True)
    thumbnail_url = models.URLField(max_length=2000, null=True, blank=True)

    created_at    = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at    = models.DateTimeField(auto_now=True)
    deleted_at    = models.DateTimeField(null=True, blank=True, db_index=True,
                                         help_text=_('Soft delete — NULL means active'))

    class Meta:
        db_table = 'construction_reports'
        ordering  = ['-created_at']
        indexes   = [
            models.Index(fields=['status']),
            models.Index(fields=['severity']),
            models.Index(fields=['deleted_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['like_count']),
            models.Index(fields=['view_count']),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.title} — {self.status}"
