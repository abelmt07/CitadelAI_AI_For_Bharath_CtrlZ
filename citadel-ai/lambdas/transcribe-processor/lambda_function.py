"""
Citadel AI - Transcribe Start Lambda
Starts a Transcribe job and returns job_name immediately.
Input: { "s3_key": "audio.mp3", "bucket": "citadel-audio-ctrlz" }
"""

import json
from uuid import uuid4
import boto3

transcribe = boto3.client("transcribe", region_name="us-east-1")

SUPPORTED_FORMATS = {"mp3": "mp3", "mp4": "mp4", "wav": "wav", "flac": "flac", "ogg": "ogg", "amr": "amr", "webm": "webm"}

def get_media_format(s3_key):
    ext = (s3_key.split(".")[-1] or "").lower()
    return SUPPORTED_FORMATS.get(ext, "mp3")

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        bucket = body.get("bucket", "citadel-audio-ctrlz")
        s3_key = body.get("s3_key", "").strip()

        if not s3_key:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Missing s3_key"})
            }

        job_name = f"citadel-{uuid4().hex[:12]}"
        media_uri = f"s3://{bucket}/{s3_key}"
        media_format = get_media_format(s3_key)

        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            IdentifyLanguage=True,
            LanguageOptions=["hi-IN", "en-IN"],
            MediaFormat=media_format,
            Media={"MediaFileUri": media_uri},
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"job_name": job_name})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }