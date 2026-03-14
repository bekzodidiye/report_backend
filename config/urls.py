from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Fuqarolar Monitoring Platform API",
      default_version='v1.0.0',
      description="GovTech civic monitoring system API",
      contact=openapi.Contact(email="support@example.uz"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

api_v1_urlpatterns = [
    path('auth/', include('apps.users.urls')),
    path('institutions/', include('apps.institutions.urls')),
    path('reports/', include('apps.reports.urls')),
    path('problems/', include('apps.problems.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('moderation/', include('apps.moderation.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_urlpatterns)),
    
    # Swagger
    re_path(r'^api/docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
