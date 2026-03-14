from apps.reports.models import Report
from apps.problems.models import Problem

class ModerationService:
    @staticmethod
    def approve_report(report_id):
        report = Report.objects.get(id=report_id)
        report.status = 'verified'
        report.save()
        return report

    @staticmethod
    def reject_problem(problem_id):
        problem = Problem.objects.get(id=problem_id)
        problem.status = 'rejected'
        problem.save()
        return problem
