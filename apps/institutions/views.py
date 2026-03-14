from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.responses import standard_response
from core.pagination import StandardPagination
from .models import Institution
from .serializers import InstitutionListSerializer, InstitutionDetailSerializer

class InstitutionListView(generics.ListAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionListSerializer
    pagination_class = StandardPagination
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60 * 5, key_prefix='institutions_list'))
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('type', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('region', openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('district', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        tags=['institutions']
    )
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filtering logic
        inst_type = request.query_params.get('type')
        region = request.query_params.get('region')
        district = request.query_params.get('district')
        
        if inst_type: queryset = queryset.filter(type=inst_type)
        if region: queryset = queryset.filter(region=region)
        if district: queryset = queryset.filter(district=district)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return standard_response(data=serializer.data)

class InstitutionDetailView(generics.RetrieveAPIView):
    queryset = Institution.objects.select_related('region', 'district').prefetch_related('promises')
    serializer_class = InstitutionDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'

    @swagger_auto_schema(tags=['institutions'])
    def get(self, request, *args, **kwargs):
        inst_id = kwargs.get('id')
        cache_key = f'institution_{inst_id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return standard_response(data=cached_data)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        cache.set(cache_key, data, 60 * 5)
        return standard_response(data=data)

class InstitutionSearchView(generics.ListAPIView):
    serializer_class = InstitutionListSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('q', openapi.IN_QUERY, type=openapi.TYPE_STRING)],
        tags=['institutions']
    )
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return standard_response(data=[])
        
        queryset = Institution.objects.filter(name__icontains=query)
        serializer = self.get_serializer(queryset, many=True)
        return standard_response(data=serializer.data)

class RegionListView(APIView):
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60 * 60, key_prefix='regions'))
    @swagger_auto_schema(tags=['institutions'])
    def get(self, request):
        regions = Institution.objects.values_list('region', flat=True).distinct()
        return standard_response(data=list(regions))

class DistrictListView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('region', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)],
        tags=['institutions']
    )
    def get(self, request):
        region = request.query_params.get('region')
        if not region:
            return standard_response(success=False, message="Region is required", status=400)
        
        cache_key = f'districts_{region}'
        districts = cache.get(cache_key)
        if not districts:
            districts = list(Institution.objects.filter(region=region).values_list('district', flat=True).distinct())
            cache.set(cache_key, districts, 60 * 60)
            
        return standard_response(data=districts)
