from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from monitor_activity.helper import generate_report, is_report_complete


class TriggerReport(APIView):
    def post(self, request):
        try:
            store_id = request.data.get('store_id')
            report_id = generate_report(store_id)
            return Response({'report_id': report_id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetReport(APIView):
    def get(self, request, report_id):
        try:
            # Check if the report generation is complete using the is_report_complete function
            report_is_complete = is_report_complete(report_id)
            if report_is_complete:
                # Return the complete report with the CSV file
                report_directory = 'reports_generated'
                report_path = "{}/{}.csv".format(report_directory, report_id)
                with open(report_path, 'r') as csv_file:
                    response = HttpResponse(csv_file, content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(report_id)
                    return response
            else:
                return Response({'status': 'Running'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
