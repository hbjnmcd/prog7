from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from polls.models import Question
from .services import get_poll_statistics
from .serializers import PollStatsSerializer


class PollStatisticsAPIView(APIView):
    """
    GET /api/analytics/polls/<id>/stats/
    """

    def get(self, request, poll_id):
        stats = get_poll_statistics(poll_id)
        serializer = PollStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PollSearchAPIView(APIView):
    """
    GET /api/analytics/polls/search/?date_from=&date_to=
    """

    def get(self, request):
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        qs = Question.objects.all()

        if date_from:
            qs = qs.filter(pub_date__gte=date_from)
        if date_to:
            qs = qs.filter(pub_date__lte=date_to)

        data = [
            {
                "id": q.id,
                "question": q.question_text,
                "pub_date": q.pub_date
            }
            for q in qs
        ]

        return Response(data)
