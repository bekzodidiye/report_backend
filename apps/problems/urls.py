from django.urls import path
from .views import ProblemCreateListView, ProblemVerifyView, ProblemDetailView

urlpatterns = [
    path('',                 ProblemCreateListView.as_view(), name='problem-list-create'),
    path('<int:id>/',        ProblemDetailView.as_view(),     name='problem-detail'),     # GET + DELETE
    path('<int:id>/verify/', ProblemVerifyView.as_view(),     name='problem-verify'),
]
