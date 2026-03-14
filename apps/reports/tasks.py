from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from apps.reports.models import Report
from apps.users.models import User
from apps.institutions.services import InstitutionService
import logging

logger = logging.getLogger(__name__)

@shared_task
def notify_moderators(report_id):
    """
    Notify moderators about a new report.
    """
    try:
        report = Report.objects.select_related('institution', 'user').get(id=report_id)
        moderators = User.objects.filter(role__in=['moderator', 'admin']).values_list('email', flat=True)
        
        if moderators:
            send_mail(
                subject=f"New Report: {report.institution.name}",
                message=f"User {report.user.email} submitted a report for {report.institution.name}.\n\nComment: {report.comment}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(moderators),
                fail_silently=True
            )
        return f"Notified {len(moderators)} moderators"
    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found for notification")

@shared_task
def update_institution_status(institution_id):
    """
    Asynchronous recalculation of institution status.
    """
    InstitutionService.update_status(institution_id)
    return f"Updated status for institution {institution_id}"
