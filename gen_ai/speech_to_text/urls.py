from django.urls import path
from .views import (
    ScheduleTranscriptionJob,
    GetTranscribedText
)

urlpatterns = [
    path('schedule-transcribe-job', ScheduleTranscriptionJob.as_view(), name='schedule_transcribe_job'),
    path('get-transcribe-text', GetTranscribedText.as_view(), name='get_transcribe_text'),
]
