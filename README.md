# Citadel AI: Your First-Strike Legal Draft
## Voice-First Legal Draft Generator for Bharat

> Transforming a Hindi voice complaint into a court-ready "Form I" in under 2 minutes.

**The Problem**: 77% of Indians cannot access legal remedies. A ₹299 fraud versus a ₹5,000 lawyer fee represents economic injustice at scale.

**The Solution**: A voice-first AI system that generates fileable consumer complaints. No lawyer required.

---

## Live Demo
- **Working Prototype**: [Your Amplify URL here]
- **Demo Video**: [YouTube link here]

---

## Quick Start (For Judges)

1. Click the **Working Prototype** link above
2. Allow microphone access when prompted
3. Tap the microphone and speak a Hindi complaint (e.g., "मुझसे हर महीने ₹299 कट रहा है")
4. Wait 30-60 seconds for processing
5. Download your Form I PDF

**Total time:** Under 2 minutes

---

## How It Works (Implemented Features)

1. **Record** — User speaks a complaint in Hindi via real-time audio capture
2. **Transcribe** — Amazon Transcribe converts speech to text
3. **Analyze** — Claude 3 on Bedrock extracts legal strategy (issue type, legal section, amount)
4. **Validate** — Simple evidence checklist (SMS proof, billing statement)
5. **Generate** — Court-compliant Form I PDF populated with user details
6. **Download** — Ready to file at consumer forum

**End-to-end processing time:** Under 2 minutes

---

## MVP Scope

| Feature | Status |
|---------|--------|
| Hindi voice recording | Working |
| Transcription via Amazon Transcribe | Working |
| Legal analysis via Claude 3 | Working |
| Evidence checklist | Working |
| Form I PDF generation | Working |
| Presigned URL download | Working |

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
| Frontend Hosting | AWS Amplify |
| User Interface | HTML + Tailwind CSS |
| Speech-to-Text | Amazon Transcribe (hi-IN) |
| Legal Analysis | Amazon Bedrock (Claude 3 Sonnet) |
| Business Logic | AWS Lambda (Python 3.9) |
| Storage | Amazon S3 |
| API Layer | Amazon API Gateway |
| Security | AWS IAM |

*Note: Architecture evolved from original design.md to prioritize rapid development within the 5-day build window.*

---

## Why AI is Required

Legal complaints require understanding context, extracting entities (amounts, dates, parties), and applying complex legal reasoning—tasks that rule-based systems cannot handle. Claude 3 on Bedrock provides the necessary intelligence to transform raw voice complaints into structured legal documents with proper citations to the Consumer Protection Act 2019.

---

## Repository Structure

```
citadel-ai/
├── frontend/
│   ├── page1-record.html
│   ├── page2-analysis.html
│   ├── page3-download.html
│   └── assets/
│       ├── microphone-icon.svg
│       └── logo.png
│
├── lambdas/
│   ├── transcribe-processor/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   ├── claude-analyzer/
│   │   ├── lambda_function.py
│   │   └── requirements.txt
│   └── pdf-generator/
│       ├── lambda_function.py
│       ├── requirements.txt
│       └── templates/
│           └── form_i_template.py
│
├── docs/
│   ├── architecture-diagram.png
│   ├── demo-script.md
│   ├── form-i-sample.pdf
│   └── test-audio/
│       ├── complaint-1.mp3
│       ├── complaint-2.mp3
│       └── complaint-3.mp3
│
├── requirements.md
├── design.md
├── README.md
└── .gitignore
```

---

## Branch Strategy

- **`main`** — Stable MVP implementation (Ramesh's telecom complaint). Protected by rulesets.
- **`feature/generalize`** — Experimental branch for multi-complaint support (work in progress)

---

## Documentation

- [Requirements & User Stories](requirements.md) (original submission)
- [System Design & Architecture](design.md) (original submission)
- [Demo Script](docs/demo-script.md)

---

## Team

| Name | Role | Responsibilities |
|------|------|------------------|
| Abel Mahesh Tharakan | Product & Legal Lead | Documentation, testing, demo video |
| Shaury Tandon | AI/ML Engineering | Claude Lambda, PDF generation |
| Aditya Nair | Cloud & Backend | AWS infrastructure, Lambdas, API Gateway, Amplify |
| Abhinav Mankar | Frontend & UX | HTML/Tailwind UI, Cursor, audio recording |

---

## Built For

**AWS AI for Bharat Hackathon**

- ✅ Generative AI on AWS (Bedrock + Claude 3)
- ✅ **Kiro for spec-driven development** (used to generate requirements and design docs)
- ✅ Serverless architecture (Lambda + S3 + API Gateway)
- ✅ Voice-first, Hindi-native design

---

## License

MIT

---

*Last updated: March 2026*
