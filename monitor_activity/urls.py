from django.urls import path
from monitor_activity.views import TriggerReport, GetReport

urlpatterns = [
    path('trigger_report/', TriggerReport.as_view(), name='trigger_report'),
    path('get_report/<str:report_id>/', GetReport.as_view(), name='get_report'),
]
