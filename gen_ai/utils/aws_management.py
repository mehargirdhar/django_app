import os
import time

import boto3
import requests
from botocore.exceptions import ClientError, NoCredentialsError


class AmazonS3:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION_NAME')        )

    def upload_file_s3_return_uri(self, local_file_path: str, bucket_name: str, object_key: str, extra_args: dict = None):
        try:
            self.s3_client.upload_file(
                local_file_path, bucket_name, object_key, ExtraArgs=extra_args)
            s3_uri = f"s3://{bucket_name}/{object_key}"
            return s3_uri
        except NoCredentialsError:
            print("Credentials not available.")
            return None
        except ClientError as e:
            print(f"Client error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None


class AmazonTranscribe:
    def __init__(self):
        self.transcribe_client = boto3.client(
            "transcribe",
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION_NAME')
        )

    def check_job_name(self, job_name):
        try:
            paginator = self.transcribe_client.get_paginator(
                'list_transcription_jobs')
            for page in paginator.paginate():
                for job in page.get('TranscriptionJobSummaries', []):
                    if job_name == job['TranscriptionJobName']:
                        response = self.transcribe_client.get_transcription_job(
                            TranscriptionJobName=job_name)
                        return response
            return None
        except Exception as e:
            print(f"Exception occurred in checking job name: {e}")
            return None

    def transcribe_audio(self, job_name, job_uri, file_format='mp3', language_code='en-IN', num_of_max_speakers=10) -> tuple[bool, str]:

        existing_job = self.check_job_name(job_name)

        if existing_job:
            print(f"Existing job found: {job_name}")
            return False, "Existing job found"

        print("Starting new transcription job...", job_name)
        transcribe_settings = {
            'TranscriptionJobName': job_name,
            'Media': {'MediaFileUri': job_uri},
            'MediaFormat': file_format,
            'LanguageCode': language_code,
            'Settings': {'ShowSpeakerLabels': True, 'MaxSpeakerLabels': num_of_max_speakers}
        }

        try:
            self.transcribe_client.start_transcription_job(
                **transcribe_settings)
            return True, "transcription began"
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConflictException':
                print(f"ConflictException: {e}")
                return False, str(e)

    def get_transcribed_audio_script(self, job_name):
        max_tries = 60
        while max_tries > 0:
            max_tries -= 1
            job = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name)
            job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]
            if job_status in ["COMPLETED", "FAILED"]:
                break
            else:
                print(
                    f"Waiting for {job_name}. Current status is {job_status}.")
            time.sleep(10)

        if job_status == "COMPLETED":
            return job['TranscriptionJob']['Transcript']['TranscriptFileUri']

        if job_status == 'FAILED':
            print(f"Transcription job failed: {job_name}")

        return None
    
    def download_transcribed_audio_script(self, job_url):
        transcript_request = requests.get(job_url)
        transcript_request.raise_for_status()
        return transcript_request.json()
    
    def parse_multiple_speaker_transcribe_json(self, transcript_json):
        items = transcript_json['results']['items']
        speaker_labels = transcript_json['results'].get('speaker_labels', None)

        if not speaker_labels:
            print("Speaker labels not available.")
            return None

        # Map speaker labels to items
        speaker_mapping = {}
        for label in speaker_labels['segments']:
            for item in label['items']:
                speaker_mapping[item['start_time']] = label['speaker_label']

        # Construct the text with speaker names
        script = []
        current_speaker = None
        current_text = []

        for item in items:
            if item['type'] == 'pronunciation':
                start_time = item['start_time']
                speaker = speaker_mapping.get(start_time, None)
                if speaker != current_speaker:
                    if current_speaker is not None:
                        script.append(f"{current_speaker}: {' '.join(current_text)}")
                    current_speaker = speaker
                    current_text = []
                current_text.append(item['alternatives'][0]['content'])

        # Append the last speaker's text
        if current_speaker is not None:
            script.append(f"{current_speaker}: {' '.join(current_text)}")

        return script
