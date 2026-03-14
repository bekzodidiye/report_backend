from rest_framework import generics, permissions, status
from rest_framework.views import APIView
import os
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.responses import standard_response
from core.permissions import IsCitizen
from core.pagination import StandardPagination
from .models import Problem
from .serializers import ProblemSerializer, ProblemCreateSerializer
from .services import ProblemService

class ProblemCreateListView(generics.ListCreateAPIView):
    queryset = Problem.objects.all().order_by('-created_at')
    serializer_class = ProblemSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsCitizen()]
        return [permissions.AllowAny()]

    @method_decorator(ratelimit(key='user', rate='10/h', method='POST', block=True))
    @swagger_auto_schema(
        request_body=ProblemCreateSerializer,
        responses={201: ProblemSerializer},
        tags=['problems']
    )
    def post(self, request, *args, **kwargs):
        serializer = ProblemCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                problem = ProblemService.create_problem(request.user, serializer.validated_data)
                return standard_response(
                    data=ProblemSerializer(problem).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return standard_response(success=False, message=str(e), status=400)
        return standard_response(success=False, errors=serializer.errors, status=400)

class ProblemVerifyView(APIView):
    permission_classes = [IsCitizen]

    @swagger_auto_schema(
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'verification_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            'status': openapi.Schema(type=openapi.TYPE_STRING)
        })},
        tags=['problems']
    )
    def post(self, request, id):
        try:
            result = ProblemService.verify_problem(id, request.user)
            return standard_response(data=result)
        except DjangoValidationError as e:
            return standard_response(success=False, message=str(e.message), status=400)
        except Exception as e:
            return standard_response(success=False, message=str(e), status=400)


class ProblemDetailView(APIView):
    """
    GET    /api/v1/problems/{id}/  — Batafsil ma'lumot
    DELETE /api/v1/problems/{id}/  — O'chirish (moderator: X-Moderator-Key header)
    """

    def _check_key(self, request):
        secret = os.getenv('MODERATOR_SECRET', '')
        return bool(secret and request.headers.get('X-Moderator-Key') == secret)

    @swagger_auto_schema(
        operation_summary="Muammo batafsil",
        responses={200: ProblemSerializer, 404: 'Topilmadi'},
        tags=['problems']
    )
    def get(self, request, id):
        try:
            problem = Problem.objects.get(pk=id)
            return standard_response(data=ProblemSerializer(problem).data)
        except Problem.DoesNotExist:
            return standard_response(success=False, message="Muammo topilmadi.", status=404)

    @swagger_auto_schema(
        operation_summary="Muammoni o'chirish (moderator)",
        operation_description="X-Moderator-Key header talab etiladi.",
        manual_parameters=[
            openapi.Parameter('X-Moderator-Key', openapi.IN_HEADER,
                              type=openapi.TYPE_STRING, required=True)
        ],
        responses={200: 'O\'chirildi', 403: 'Ruxsat berilmagan', 404: 'Topilmadi'},
        tags=['problems']
    )
    def delete(self, request, id):
        if not self._check_key(request):
            return standard_response(success=False, message="Ruxsat berilmagan.", status=403)
        try:
            problem = Problem.objects.get(pk=id)
            problem.delete()
            return standard_response(message="Muammo muvaffaqiyatli o'chirildi.")
        except Problem.DoesNotExist:
            return standard_response(success=False, message="Muammo topilmadi.", status=404)
