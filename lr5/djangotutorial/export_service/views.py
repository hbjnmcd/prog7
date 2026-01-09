from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status

from analytics.services import get_poll_statistics
from .utils import poll_stats_to_csv


class PollExportAPIView(APIView):
    """
    GET /api/export/polls/<id>/?format=json|csv
    """

    def get(self, request, poll_id):
        export_format = request.query_params.get("format", "json")
        stats = get_poll_statistics(poll_id)

        if export_format == "json":
            return Response(stats, status=status.HTTP_200_OK)

        if export_format == "csv":
            csv_data = poll_stats_to_csv(stats)
            response = HttpResponse(csv_data, content_type="text/csv")
            response["Content-Disposition"] = (
                f'attachment; filename="poll_{poll_id}.csv"'
            )
            return response

        return Response(
            {"error": "Unsupported format"},
            status=status.HTTP_400_BAD_REQUEST
        )
