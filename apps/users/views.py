from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.responses import standard_response
from .serializers import UserSerializer, RegisterSerializer, UserMeSerializer

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: UserSerializer},
        tags=['auth']
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            data = UserSerializer(user).data
            data['tokens'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return standard_response(
                success=True,
                data=data,
                message="Registration successful",
                status=status.HTTP_201_CREATED
            )
        return standard_response(
            success=False,
            message="Registration failed",
            errors=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class UserMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserMeSerializer},
        tags=['auth']
    )
    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return standard_response(data=serializer.data)

    @swagger_auto_schema(
        request_body=UserMeSerializer,
        responses={200: UserMeSerializer},
        tags=['auth']
    )
    def patch(self, request):
        serializer = UserMeSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return standard_response(data=serializer.data)
        return standard_response(
            success=False,
            errors=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=['auth']
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return standard_response(message="Logged out successfully")
        except Exception:
            return standard_response(success=False, message="Invalid token", status=status.HTTP_400_BAD_REQUEST)

class FileUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'file', openapi.IN_FORM, type=openapi.TYPE_FILE, 
                description='Image to upload (max 5MB, jpg/png)'
            )
        ],
        tags=['upload']
    )
    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return standard_response(success=False, message="No file provided", status=400)
        
        # Validation
        if file_obj.size > 5 * 1024 * 1024:
            return standard_response(success=False, message="File too large", status=400)
        
        content_type = file_obj.content_type
        if content_type not in ['image/jpeg', 'image/png']:
            return standard_response(success=False, message="Only JPG and PNG are allowed", status=400)

        # In a real app with django-storages, saving it to a model field handles S3.
        # Here we just return a mock URL if no storage is backend yet, or handle manual upload.
        # For completeness, let's assume we use a temporary model or just return the static URL if local.
        # But per requirements, it should be S3.
        
        from django.core.files.storage import default_storage
        from core.utils import rename_file_to_uuid
        
        filename = rename_file_to_uuid(None, file_obj.name)
        path = default_storage.save(f"uploads/{filename}", file_obj)
        url = default_storage.url(path)
        
        return standard_response(data={"url": url})
