from django.core.cache import cache
from apps.institutions.models import Institution
from apps.problems.models import Problem

class InstitutionService:
    @staticmethod
    def update_status(institution_id):
        """
        Update institution status based on verified problems.
        0 verified → green
        1-3 verified → yellow
        4+ verified → red
        """
        count = Problem.objects.filter(
            institution_id=institution_id,
            status=Problem.VERIFIED
        ).count()

        if count == 0:
            status = Institution.GREEN
        elif count <= 3:
            status = Institution.YELLOW
        else:
            status = Institution.RED

        Institution.objects.filter(id=institution_id).update(status=status)
        
        # Invalidate cache
        cache.delete(f'institution_{institution_id}')
        cache.delete('dashboard_stats')
        cache.delete('dashboard_map')
