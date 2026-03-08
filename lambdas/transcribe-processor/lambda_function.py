"""
Citadel AI - Transcribe Pipeline Lambda (citadel-transcribe-processor)
Starts Amazon Transcribe job for Hindi (hi-IN), polls until complete, returns transcript.
Input: { "s3_key": "audio.mp3", "bucket": "citadel-audio-ctrlz" }
"""

import json
import time
import urllib.request
from uuid import uuid4

import boto3

# Clients
transcribe = boto3.client("transcribe", region_name="us-east-1")
s3 = boto3.client("s3", region_name="us-east-1")

# Config
POLL_INTERVAL_SEC = 3
MAX_WAIT_SEC = 300  # 5 min
SUPPORTED_FORMATS = {"mp3": "mp3", "mp4": "mp4", "wav": "wav", "flac": "flac", "ogg": "ogg", "amr": "amr", "webm": "webm"}


def get_media_format(s3_key: str) -> str:
    """Infer Transcribe MediaFormat from file extension."""
    ext = (s3_key.split(".")[-1] or "").lower()
    return SUPPORTED_FORMATS.get(ext, "mp3")


def get_transcript_from_uri(uri: str) -> str:
    """
    Fetch transcript JSON from S3 URI and return transcript text.
    URI format: s3://bucket/key
    """
    if not uri.startswith("s3://"):
        # If it's an HTTPS pre-signed URL, fetch directly
        with urllib.request.urlopen(uri, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return (data.get("results", {}).get("transcripts") or [{}])[0].get("transcript", "")

    # Parse s3://bucket/key
    parts = uri.replace("s3://", "").split("/", 1)
    bucket = parts[0]
    key = parts[1]
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(obj["Body"].read().decode())
    return (data.get("results", {}).get("transcripts") or [{}])[0].get("transcript", "")


def lambda_handler(event, context):
    """
    Expected event: { "s3_key": "audio.mp3", "bucket": "citadel-audio-ctrlz" }
    Returns: { "transcript": "..." } or error payload.
    """
    try:
        bucket = (event.get("bucket") or "").strip() or "citadel-audio-ctrlz"
        s3_key = (event.get("s3_key") or "").strip()
        if not s3_key:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing s3_key"}),
                "headers": {"Content-Type": "application/json"},
            }

        media_uri = f"s3://{bucket}/{s3_key}"
        media_format = get_media_format(s3_key)
        job_name = f"citadel-{uuid4().hex[:12]}"

        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode="hi-IN",
            MediaFormat=media_format,
            Media={"MediaFileUri": media_uri},
        )

        # Poll until complete or timeout
        start = time.time()
        while True:
            if time.time() - start > MAX_WAIT_SEC:
                transcribe.delete_transcription_job(TranscriptionJobName=job_name)
                return {
                    "statusCode": 408,
                    "body": json.dumps({"error": "Transcription job timed out"}),
                    "headers": {"Content-Type": "application/json"},
                }

            job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            status = job["TranscriptionJob"]["TranscriptionJobStatus"]

            if status == "COMPLETED":
                transcript_uri = job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
                transcript_text = get_transcript_from_uri(transcript_uri)
                return {
                    "statusCode": 200,
                    "body": json.dumps({"transcript": transcript_text}),
                    "headers": {"Content-Type": "application/json"},
                }

            if status == "FAILED":
                reason = job["TranscriptionJob"].get("FailureReason", "Unknown")
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": f"Transcription failed: {reason}"}),
                    "headers": {"Content-Type": "application/json"},
                }

            time.sleep(POLL_INTERVAL_SEC)

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"},
        }