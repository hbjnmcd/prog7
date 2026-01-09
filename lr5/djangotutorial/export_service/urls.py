from django.urls import path
from .views import PollExportAPIView

urlpatterns = [
    path("polls/<int:poll_id>/", PollExportAPIView.as_view()),
]
