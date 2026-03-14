from django.urls import path
from .views import DashboardStatsView, DashboardMapView, TopUsersView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('map/', DashboardMapView.as_view(), name='dashboard-map'),
    path('top-users/', TopUsersView.as_view(), name='dashboard-top-users'),
]
