from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_yasg.utils import swagger_auto_schema
from core.responses import standard_response
from core.permissions import IsCitizen
from core.pagination import StandardPagination
from .models import Report
from .serializers import ReportSerializer, ReportCreateSerializer
from .services import ReportService

@method_decorator(name='post', decorator=ratelimit(key='user', rate='10/h', method='POST', block=True))
class ReportCreateListView(generics.ListCreateAPIView):
    queryset = Report.objects.all().order_by('-created_at')
    serializer_class = ReportSerializer
    pagination_class = StandardPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsCitizen()]
        return [permissions.AllowAny()]

    @swagger_auto_schema(
        request_body=ReportCreateSerializer,
        responses={201: ReportSerializer},
        tags=['reports']
    )
    def post(self, request, *args, **kwargs):
        serializer = ReportCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                report = ReportService.create_report(request.user, serializer.validated_data)
                return standard_response(
                    data=ReportSerializer(report).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return standard_response(success=False, message=str(e), status=400)
        return standard_response(success=False, errors=serializer.errors, status=400)

class ReportVerifyView(APIView):
    permission_classes = [IsCitizen]

    @swagger_auto_schema(
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'verification_count': openapi.Schema(type=openapi.TYPE_INTEGER),
            'status': openapi.Schema(type=openapi.TYPE_STRING)
        })},
        tags=['reports']
    )
    def post(self, request, id):
        try:
            result = ReportService.verify_report(id, request.user)
            return standard_response(data=result)
        except DjangoValidationError as e:
            return standard_response(success=False, message=str(e.message), status=400)
        except Exception as e:
            return standard_response(success=False, message=str(e), status=400)
