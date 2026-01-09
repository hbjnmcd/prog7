from django.urls import path
from .views import PollStatisticsAPIView, PollSearchAPIView

urlpatterns = [
    path("polls/<int:poll_id>/stats/", PollStatisticsAPIView.as_view()),
    path("polls/search/", PollSearchAPIView.as_view()),
]
