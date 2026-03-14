from django.db.models import F
from django.core.exceptions import ValidationError
from apps.reports.models import Report, ReportVerification
from apps.users.services import ReputationService
from apps.reports.tasks import notify_moderators, update_institution_status

class ReportService:
    @staticmethod
    def create_report(user, validated_data):
        """
        Create a report and trigger notifications.
        """
        report = Report.objects.create(user=user, **validated_data)
        # Notify moderators asynchronously
        notify_moderators.delay(report.id)
        return report

    @staticmethod
    def verify_report(report_id, user):
        """
        Verify a report. 
        Increments verification count. 
        If count reaches 3, report is verified and author gets points.
        """
        report = Report.objects.select_related('user', 'institution').get(id=report_id)

        if ReportVerification.objects.filter(report=report, user=user).exists():
            raise ValidationError("You have already verified this report.")

        if report.user == user:
            raise ValidationError("You cannot verify your own report.")

        ReportVerification.objects.create(report=report, user=user)
        
        # Increment verification count
        report.verification_count = F('verification_count') + 1
        report.save(update_fields=['verification_count'])
        report.refresh_from_db()

        if report.verification_count >= 3:
            Report.objects.filter(id=report.id).update(status=Report.VERIFIED)
            ReputationService.add_points(report.user, 'report_verified', 20)
            # Recalculate institution status
            update_institution_status.delay(report.institution_id)

        return {"verification_count": report.verification_count, "status": report.status}

    @staticmethod
    def reject_report(report_id, moderator):
        """
        Reject a report. Author loses points.
        """
        report = Report.objects.select_related('user').get(id=report_id)
        report.status = Report.REJECTED
        report.save(update_fields=['status'])
        
        ReputationService.add_points(report.user, 'report_rejected', -5)
        return report
