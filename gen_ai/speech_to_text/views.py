import os
import requests

from django.core.files.storage import default_storage
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from utils.aws_management import AmazonS3,AmazonTranscribe

class ScheduleTranscriptionJob(APIView):
    def post(self, request):
        # try:
            mp3_file = request.FILES['file']
            file_path = default_storage.save(mp3_file.name, mp3_file)

            s3_client = AmazonS3()
            s3_uri_mp3_file = s3_client.upload_file_s3_return_uri(
                local_file_path=file_path,
                bucket_name=os.getenv('AWS_S3_BUCKET_NAME'),
                object_key=f"{os.getenv('AWS_S3_BUCKET_TEMP_KEY')}/{mp3_file.name}"
            )

            if not s3_uri_mp3_file:
                return Response(
                        data={"status": False, "message":"Something went wrong while uploading recording to s3"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            transcribe_client = AmazonTranscribe()
            job_status, message = transcribe_client.transcribe_audio(
                job_name=mp3_file.name,
                job_uri=s3_uri_mp3_file
            )

            os.remove(file_path)

            if job_status:
                return Response(
                    data={"message": message, "status":True}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                        data={"status": False, "message":message},
                        status=status.HTTP_400_BAD_REQUEST
                )
            
        # except Exception as error:
# 
            # return Response(
                # data={"status": False, "message":str(error)},
                # status=status.HTTP_500_INTERNAL_SERVER_ERROR
            # )

class GetTranscribedText(APIView):
     def post(self, request):
        job_name = request.data.get('job_name')

        transcribe_client = AmazonTranscribe()
        job_url = transcribe_client.get_transcribed_audio_script(job_name=job_name)
        if not job_url:
            return None
        

        transcript_json = transcribe_client.download_transcribed_audio_script(job_url=job_url)

        transcribe_text = transcribe_client.parse_multiple_speaker_transcribe_json(transcript_json=transcript_json)

        return Response(data=transcribe_text)

