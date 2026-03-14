from django.db import models
from django.utils.translation import gettext_lazy as _
from core.mixins import TimeStampedModel

class Institution(TimeStampedModel):
    SCHOOL = 'school'
    KINDERGARTEN = 'kindergarten'
    SSV = 'ssv'

    TYPE_CHOICES = [
        (SCHOOL, _('School')),
        (KINDERGARTEN, _('Kindergarten')),
        (SSV, _('SSV Institution')),
    ]

    GREEN = 'green'
    YELLOW = 'yellow'
    RED = 'red'

    STATUS_CHOICES = [
        (GREEN, _('Green')),
        (YELLOW, _('Yellow')),
        (RED, _('Red')),
    ]

    external_id = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=300)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    region = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=GREEN)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['region', 'district']),
            models.Index(fields=['status']),
            models.Index(fields=['name']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.region})"
