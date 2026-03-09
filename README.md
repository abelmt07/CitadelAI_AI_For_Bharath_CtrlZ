# Citadel AI: Your First-Strike Legal Draft
## Voice-First Legal Draft Generator for Bharat

> Transforming a Hindi voice complaint into a court-ready "Form I" in under 2 minutes.

**The Problem**: 77% of Indians cannot access legal remedies. A ₹299 fraud versus a ₹5,000 lawyer fee represents economic injustice at scale.

**The Solution**: A voice-first AI system that generates fileable consumer complaints. No lawyer required.

---

## Live Demo

- **Working Prototype**:  https://citai.vercel.app/
- **Demo Video**: https://youtu.be/ISkvOVzXVIg

---

## Quick Start (For Judges)

1. Click the **Working Prototype** link above  
2. Allow microphone access when prompted  
3. Tap the microphone and speak a Hindi complaint (e.g., "मुझसे हर महीने ₹299 कट रहा है")  
4. Wait 30–60 seconds for processing  
5. Download your Form I PDF  

**Total time:** Under 2 minutes

---

## How It Works (Implemented Features)

1. **Record** — User speaks a complaint in Hindi via real-time audio capture (`index.html`)  
2. **Transcribe** — Amazon Transcribe converts speech to text (`lambdas/transcribe-processor/lambda_function.py`)  
3. **Analyze** — **Amazon Nova Lite** on Bedrock extracts legal strategy (`lambdas/nova-analyzer/lambda_function.py`)  
4. **Validate** — Dynamic evidence checklist tailored to the issue type (frontend logic)  
5. **Generate** — Court-compliant Form I PDF populated with extracted details (`lambdas/pdf-generator/lambda_function.py`)  
6. **Download** — Ready to file at consumer forum  

**End-to-end processing time:** Under 2 minutes (typically 60 seconds)

---

## MVP Scope

| Feature | Status |
|--------|--------|
| Hindi voice recording | ✅ Working |
| Transcription via Amazon Transcribe | ✅ Working |
| Legal analysis via **Amazon Nova Lite** | ✅ Working |
| Dynamic evidence checklist | ✅ Working |
| Form I PDF generation (with dynamic fields) | ✅ Working |
| Presigned URL download | ✅ Working |
| **Generalization** – works for telecom, e‑commerce, food delivery, banking, etc. | ✅ Implemented |

### Features Excluded from MVP

- Cohere Embed (hardcoded Consumer Protection Act sections used instead)  
- Amazon Q orchestration (direct Lambda calls implemented)  
- DynamoDB session state (in-memory only)  
- Multi-language support (Hindi only)  
- Real-time streaming (batch upload)  

---

## Technology Stack

| Component | Service |
|-----------|---------|
| Frontend Hosting | **Vercel** |
| User Interface | HTML + Tailwind CSS (`index.html` at root) |
| Speech-to-Text | Amazon Transcribe (hi-IN) – `lambdas/transcribe-processor/` |
| Legal Analysis | **Amazon Nova Lite** on Bedrock – `lambdas/nova-analyzer/` |
| PDF Generation | AWS Lambda (Python 3.9) – `lambdas/pdf-generator/` |
| Storage | Amazon S3 |
| API Layer | Amazon API Gateway |
| Security | AWS IAM |

*Note: Lambda functions are organized by purpose under the `lambdas/` directory, each with its own `lambda_function.py`.*

---

## Why AI is Required

Legal complaints require understanding context, extracting entities (amounts, dates, parties), and applying complex legal reasoning—tasks that rule-based systems cannot handle. **Amazon Nova Lite** on Bedrock provides the necessary intelligence to transform raw voice complaints into structured legal documents with proper citations to the Consumer Protection Act 2019.

---

## Repository Structure

After reorganization, the repository is clean and logically grouped:

```

citadel-ai/
├── .gitignore
├── README.md
├── requirements.md
├── design.md
├── context.md
├── index.html # Main frontend entry point
├── docs/
│ ├── demo-script.md
│ ├── form-i-sample.pdf
│ ├── TeamCtrlZ_CitadelAI_AI_for_Bharat.pdf
│ └── test-audio/
│ ├── recording1.m4a
│ ├── recording2.m4a
│ ├── recording3.m4a
│ └── expected_outcomes.txt
├── frontend/
│ └── assets/
│ └── logo.png
└── lambdas/
├── transcribe-processor/
│ └── lambda_function.py
├── nova-analyzer
│ └── lambda_function.py
├── pdf-generator/
│ └── lambda_function.py

```
---

## Branch Strategy

- **`main`** — Stable generalized MVP (works for multiple complaint types). Protected by rulesets.  
- *(All development now on `main`; feature branches are merged.)*

---

## Documentation

- [Requirements & User Stories](requirements.md) (original submission)  
- [System Design & Architecture](design.md) (original submission)  
- [Demo Script](docs/demo-script.md)  

---

## Team

| Name | Role | Responsibilities |
|------|------|------------------|
| Abel Mahesh Tharakan | Integration & Strategy Lead | Documentation, testing, team coordination, demo video |
| Shaury Tandon | AI/ML Engineering | **Nova Lite** Lambda, PDF generation, prompt engineering |
| Aditya Nair | Cloud & Backend | AWS infrastructure, Lambda functions, API Gateway, Vercel hosting |
| Abhinav Mankar | Frontend & UX | HTML/Tailwind UI, Cursor, audio recording, evidence validator |

---

## Built For

**AWS AI for Bharat Hackathon**

- ✅ Generative AI on AWS (Bedrock + **Nova Lite**)  
- ✅ Kiro for spec-driven development (used to generate requirements and design docs)  
- ✅ Serverless architecture (Lambda + S3 + API Gateway)  
- ✅ Voice-first, Hindi-native design  

---

## License

MIT

---

*Last updated: March 2026*
