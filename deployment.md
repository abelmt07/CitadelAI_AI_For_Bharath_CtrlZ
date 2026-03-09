# Citadel AI – Deployment Guide

This document provides step-by-step instructions to deploy Citadel AI locally or to production.

---

## Prerequisites

- **AWS Account** with access to:
  - Amazon Transcribe
  - Amazon Bedrock (Nova Lite)
  - AWS Lambda
  - Amazon API Gateway
  - Amazon S3
    
- **Python 3.9+** installed
  
- **Node.js** (optional, for frontend)
  
- **Vercel account** (for frontend hosting)
  
- **Git** (to clone the repository)

---

## Backend Deployment (AWS Lambda + API Gateway)


### 1. Clone the Repository

```bash
git clone https://github.com/abelmt07/CitadelAI_AI_For_Bharath_CtrlZ.git
cd citadel-ai
```


### 2. Set up AWS Credentials

Configure your AWS CLI:

```bash
aws configure
# Enter your Access Key, Secret Key, region (ap-south-1 recommended)
```


### 3. Create S3 Buckets

```bash
aws s3 mb s3://citadel-audio-[your-team-name]
aws s3 mb s3://citadel-pdfs-[your-team-name]
```


### 4. Deploy Lambda Functions

#### Transcribe Processor Lambda

```bash
cd lambdas/transcribe-processor
pip install -r requirements.txt -t ./package
cp lambda_function.py package/
cd package
zip -r ../transcribe-processor.zip .
aws lambda create-function \
  --function-name citadel-transcribe-processor \
  --runtime python3.9 \
  --role arn:aws:iam::[YOUR-ACCOUNT-ID]:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://transcribe-processor.zip \
  --memory-size 256 \
  --timeout 30
```


#### Nova Analyzer Lambda

```bash
cd ../claude-analyzer  # folder name kept for historical reasons – contains Nova Lite code
pip install -r requirements.txt -t ./package
cp lambda_function.py package/
cd package
zip -r ../nova-analyzer.zip .
aws lambda create-function \
  --function-name citadel-nova-analyzer \
  --runtime python3.9 \
  --role arn:aws:iam::[YOUR-ACCOUNT-ID]:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://nova-analyzer.zip \
  --memory-size 1024 \
  --timeout 60
```


#### PDF Generator Lambda

```bash
cd ../pdf-generator
pip install -r requirements.txt -t ./package
cp lambda_function.py package/
cd package
zip -r ../pdf-generator.zip .
aws lambda create-function \
  --function-name citadel-pdf-generator \
  --runtime python3.9 \
  --role arn:aws:iam::[YOUR-ACCOUNT-ID]:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://pdf-generator.zip \
  --memory-size 1024 \
  --timeout 30
```


### 5. Set Up API Gateway

1. Go to AWS Console → API Gateway

2. Create a new REST API named citadel-api

3. Create resources and methods:

   - `POST /transcribe` → citadel-transcribe-processor

   - `POST /analyze` → citadel-nova-analyzer

   - `POST /generate` → citadel-pdf-generator

4. Enable CORS for all methods

5. Deploy API to a stage (e.g., prod)

6. Note the Invoke URL (e.g., ```https://api-id.execute-api.ap-south-1.amazonaws.com/prod```)

---

## 🌐 Frontend Deployment (Vercel)

### 1. Configure Environment Variables

Create a .env file in the frontend/ directory (see .env.example).


### 2. Deploy to Vercel

```bash
npm install -g vercel
cd frontend
vercel
```

Follow the prompts. Vercel will automatically detect the HTML project and provide a live URL.


### 3. Update API Endpoints

Ensure your ```frontend/index.html``` points to the correct API Gateway URL.

---

## ✅ Verification


1. Open your Vercel URL

2. Allow microphone access

3. Speak a Hindi/English complaint (e.g., "एयरटेल ने बिना पूछे ₹299 काट लिया")

4. Verify:

    - Transcription appears

    - Analysis shows correct issue, company, amount, section

    - PDF generates and downloads

5. Total time should be under 2 minutes

---

    
## 🧹 Cleanup

To avoid incurring costs, delete resources when done:

```bash
aws lambda delete-function --function-name citadel-transcribe-processor
aws lambda delete-function --function-name citadel-nova-analyzer
aws lambda delete-function --function-name citadel-pdf-generator
# Delete API Gateway and S3 buckets via console
```

---

## 🆘 Troubleshooting


| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| `AccessDeniedException` | IAM role missing permissions | Attach `AmazonTranscribeFullAccess`, `AmazonBedrockFullAccess`, `AmazonS3FullAccess` policies. |
| API Gateway timeout | Lambda execution too slow | Increase Lambda timeout (max 900s) or memory allocation. |
| CORS error in browser | API Gateway CORS not enabled | Enable CORS for each resource and redeploy API. |
| PDF generation fails | ReportLab missing in package | Ensure `reportlab` in `requirements.txt` and included in deployment zip. |
| Transcribe job stuck | Audio format not supported | Use MP3, WAV, or FLAC. File size < 2GB. Check region limits. |
| Bedrock returns gibberish | Incorrect model ID or prompt format | Verify Nova Lite model ID. Test prompt in AWS Console first. |
| Frontend cannot reach API | Wrong API Gateway URL | Double-check invoke URL includes stage (e.g., `/prod`). Test with `curl`. |
| S3 presigned URL AccessDenied | Lambda lacks S3 permissions | Add `s3:PutObject` and `s3:GetObject` to Lambda role. |
| Microphone fails in browser | HTTPS required or permission denied | Serve over HTTPS. Check browser microphone permissions. |

---

For more help, open an issue on GitHub.
