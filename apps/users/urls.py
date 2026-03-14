from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, UserMeView, LogoutView, FileUploadView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenRefreshView.as_view(), name='login'), # Note: Usually TokenObtainPairView
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserMeView.as_view(), name='me'),
    path('upload/', FileUploadView.as_view(), name='upload'),
]
