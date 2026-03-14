from django.urls import path
from .views import ProblemCreateListView, ProblemVerifyView

urlpatterns = [
    path('', ProblemCreateListView.as_view(), name='problem-list-create'),
    path('<int:id>/verify/', ProblemVerifyView.as_view(), name='problem-verify'),
]
