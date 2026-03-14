from django_filters import rest_framework as filters
from .models import Institution

class InstitutionFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    region = filters.CharFilter(lookup_expr='iexact')
    district = filters.CharFilter(lookup_expr='iexact')
    type = filters.CharFilter(lookup_expr='iexact')
    status = filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Institution
        fields = ['type', 'region', 'district', 'status', 'name']
