import boto3
import json
from uuid import uuid4

s3 = boto3.client("s3", region_name="us-east-1")
BUCKET = "citadel-audio-ctrlz"

def lambda_handler(event, context):
    try:
        file_name = f"audio-{uuid4().hex[:8]}.mp3"
        
        presigned_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": BUCKET,
                "Key": file_name,
                "ContentType": "audio/webm"
            },
            ExpiresIn=300  # 5 minutes
        )
        
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "upload_url": presigned_url,
                "s3_key": file_name,
                "bucket": BUCKET
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }