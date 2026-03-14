from django.urls import path
from .views import (
    InstitutionListView, InstitutionDetailView, InstitutionSearchView,
    RegionListView, DistrictListView
)

urlpatterns = [
    path('', InstitutionListView.as_view(), name='institution-list'),
    path('search/', InstitutionSearchView.as_view(), name='institution-search'),
    path('regions/', RegionListView.as_view(), name='region-list'),
    path('districts/', DistrictListView.as_view(), name='district-list'),
    path('<int:id>/', InstitutionDetailView.as_view(), name='institution-detail'),
]
