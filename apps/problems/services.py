from django.db.models import F
from django.core.exceptions import ValidationError
from apps.problems.models import Problem, ProblemVerification
from apps.users.services import ReputationService
from apps.reports.tasks import update_institution_status

class ProblemService:
    @staticmethod
    def create_problem(user, validated_data):
        return Problem.objects.create(user=user, **validated_data)

    @staticmethod
    def verify_problem(problem_id, user):
        problem = Problem.objects.select_related('user', 'institution').get(id=problem_id)

        if ProblemVerification.objects.filter(problem=problem, user=user).exists():
            raise ValidationError("Already verified")

        if problem.user == user:
            raise ValidationError("Cannot verify own problem")

        ProblemVerification.objects.create(problem=problem, user=user)
        problem.verification_count = F('verification_count') + 1
        problem.save(update_fields=['verification_count'])
        problem.refresh_from_db()

        if problem.verification_count >= 3:
            Problem.objects.filter(id=problem.id).update(status=Problem.VERIFIED)
            ReputationService.add_points(problem.user, 'report_verified', 20)
            update_institution_status.delay(problem.institution_id)

        return {"verification_count": problem.verification_count, "status": problem.status}
