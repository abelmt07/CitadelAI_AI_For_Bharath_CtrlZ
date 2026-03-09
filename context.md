# Citadel AI - Project Context
## Read this before helping me with ANYTHING in this project.

## Project Identity
- Name: Citadel AI
- Tagline: "Your First-Strike Legal Draft"
- Core promise: Hindi voice → court-ready Form I draft in 120 seconds
- Target user: Ramesh, a shopkeeper in Lucknow with unauthorized ₹299 telecom charges
- Hackathon: AI for Bharat by AWS

## Team
- Abel Mahesh Tharakan – Lead + integration (little Python)
- Aditya Nair – Cloud + AWS setup (good Python)
- Shaury Tandon – AI + PDF generation (good Python)
- Abhinav Mankar – Frontend HTML (learning)
- All first-time AWS users. 5 days to build.

## The Problem
77% of India excluded from legal system.
₹299 fraud requires ₹5000 lawyer = economic injustice.
50M+ unheard complaints.

## The Solution
Voice-first AI that turns a Hindi complaint into a 
court-ready Form I in 120 seconds. No lawyer needed.

## Tech Stack
- Frontend: Single HTML file + Tailwind CDN + Font Awesome CDN
- Backend: Python Lambda functions (3 total)
- Voice: Amazon Transcribe (Hindi, hi-IN)
- AI: Amazon Bedrock (Claude 3 Sonnet)
- PDF: ReportLab Python library
- Storage: AWS S3 (us-east-1)
- API: AWS API Gateway connecting frontend to Lambdas
- Region: us-east-1 (N. Virginia) for everything

## AWS Services
- S3 buckets: citadel-audio-ctrlz, citadel-pdfs-ctrlz
- Lambda role: citadel-lambda-role
- Region: us-east-1

## 3 Lambda Functions
1. citadel-transcribe-processor
   - Input: { "s3_key": "audio.mp3", "bucket": "citadel-audio-ctrlz" }
   - Starts Hindi Transcribe job, polls until complete
   - Returns: transcript text

2. citadel-analyze-claude  
   - Input: transcript text
   - Calls Bedrock Claude 3 Sonnet with hardcoded CPA sections
   - Returns JSON: { issue, section, relief, party, amount }

3. citadel-generate-pdf
   - Input: Claude JSON + user details
   - Generates Form I PDF using ReportLab
   - Uploads to S3, returns presigned download URL

## Consumer Protection Act Sections (hardcoded in Claude prompt)
- Section 2(47): Unfair trade practice
- Section 35: Filing complaint
- Section 42: Compensation

## The One Flow That Must Work (MVP)
Ramesh records Hindi complaint about ₹299 telecom charge
→ Audio uploads to S3
→ Transcribe converts Hindi speech to text
→ Claude analyzes and returns legal JSON
→ ReportLab generates Form I PDF
→ Ramesh downloads PDF

## What's CUT from MVP
- No DynamoDB (use in-memory)
- No real-time streaming (batch upload)
- No multi-language (Hindi only)
- No full evidence validator (2 hardcoded questions)
- No Amazon Q

## UI Design
- 3 screens: Chat/Voice Input → AI Analysis → Form I Preview
- Dark green color scheme (#1B4332)
- Mobile-first
- Font: Inter (Google Fonts CDN)
- Icons: Font Awesome CDN
- Looks like a consumer product, not a dashboard

## Success Criteria by Day 5
- Audio upload → transcription works
- Claude returns correct JSON
- PDF generates with real data
- Download works
- Demo video recorded
- GitHub repo with code
- Live URL accessible (HTML hosted on S3)

## Golden Rule
Only Ramesh's telecom complaint needs to work. Nothing else.
80% perfect is winning. Prioritize working demo over elegant code.
When stuck: hardcode it, fake it, or record the video another way.

## How to Help Me
- Assume first-time AWS user
- Give copy-paste ready code always
- Include exact AWS console steps when needed
- Anticipate common errors and mention fixes
- Stay within the 5-day MVP scope
- Never suggest features that are cut