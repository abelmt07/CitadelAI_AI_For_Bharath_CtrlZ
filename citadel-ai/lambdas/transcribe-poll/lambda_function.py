"""
Citadel AI - Transcribe Poll Lambda
Checks job status once. Returns transcript or PROCESSING.
Input: { "job_name": "citadel-abc123" }
"""

import json
import urllib.request
import boto3

transcribe = boto3.client("transcribe", region_name="us-east-1")
s3 = boto3.client("s3", region_name="us-east-1")

def get_transcript_from_uri(uri):
    if not uri.startswith("s3://"):
        with urllib.request.urlopen(uri, timeout=30) as resp:
            data = json.loads(resp.read().decode())
        return (data.get("results", {}).get("transcripts") or [{}])[0].get("transcript", "")
    
    parts = uri.replace("s3://", "").split("/", 1)
    obj = s3.get_object(Bucket=parts[0], Key=parts[1])
    data = json.loads(obj["Body"].read().decode())
    return (data.get("results", {}).get("transcripts") or [{}])[0].get("transcript", "")

def lambda_handler(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        job_name = params.get("job_name", "").strip()

        if not job_name:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Missing job_name"})
            }

        job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        status = job["TranscriptionJob"]["TranscriptionJobStatus"]

        if status == "COMPLETED":
            uri = job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
            transcript = get_transcript_from_uri(uri)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"status": "COMPLETED", "transcript": transcript})
            }

        if status == "FAILED":
            reason = job["TranscriptionJob"].get("FailureReason", "Unknown")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"status": "FAILED", "error": reason})
            }

        # Still IN_PROGRESS
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"status": "PROCESSING"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }