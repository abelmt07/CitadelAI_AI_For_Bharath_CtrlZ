# Citadel AI: Your First-Strike Legal Draft
### Voice-First Legal Draft Generator for Bharat

> **Transforming a Hindi voice complaint into a court-ready "Form I" in under 2 minutes.**

**The Problem**: 77% of Indians can't access legal remedies. A ₹299 fraud vs. a ₹5,000 lawyer fee = economic injustice.

**The Solution**: Voice-first AI that generates fileable consumer complaints. No lawyer required.

---

## 🚀 Live Demo
- **Working Prototype**: [Your Amplify URL here]
- **Demo Video**: [YouTube link here]

---

## ⚡ How It Works (What We Built)

1. **🎤 Record** — User speaks a complaint in Hindi (real-time audio capture)
2. **📝 Transcribe** — Amazon Transcribe converts speech to text
3. **🧠 Analyze** — Claude 3 on Bedrock extracts legal strategy (issue type, section, amount)
4. **✅ Validate** — Simple evidence checklist (SMS proof, billing statement)
5. **📄 Generate** — Court-compliant Form I PDF with user details
6. **⬇️ Download** — Ready to file at consumer forum

**End-to-end time:** Under 2 minutes

---

## 🎯 MVP Scope (What Works)

| Feature | Status |
|---------|--------|
| Hindi voice recording | ✅ Working |
| Transcription via Transcribe | ✅ Working |
| Legal analysis via Claude 3 | ✅ Working |
| Evidence checklist | ✅ Working |
| Form I PDF generation | ✅ Working |
| Download via presigned URL | ✅ Working |

### What's Cut (for MVP)
- ❌ Cohere Embed (hardcoded CPA sections)
- ❌ Amazon Q orchestration (direct Lambda calls)
- ❌ DynamoDB session state (in-memory only)
- ❌ Multi-language support (Hindi only)
- ❌ Real-time streaming (batch upload)

---

## 🏗️ Tech Stack (AWS Native - What We Actually Used)

| Component | Service |
|-----------|---------|
| **Frontend** | HTML + Tailwind CSS (hosted on AWS Amplify) |
| **Voice → Text** | Amazon Transcribe (hi-IN) |
| **Legal Analysis** | Amazon Bedrock (Claude 3 Sonnet) |
| **Business Logic** | AWS Lambda (Python 3.9) |
| **Storage** | Amazon S3 (audio + PDFs) |
| **API Layer** | Amazon API Gateway |
| **Hosting** | AWS Amplify |
| **Security** | AWS IAM |

*Note: Architecture evolved from original design.md to prioritize buildability within 5 days.*

---

## 📂 Repository Structure

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
├── .github/
│   └── workflows/
│       └── (future CI/CD if added)
│
├── requirements.md
├── design.md
├── README.md
└── .gitignore

---

## 🌿 Branch Strategy

- **`main`** — Stable MVP (Ramesh's telecom complaint). Protected by rulesets.
- **`feature/generalize`** — Experimental multi-complaint support (WIP)

---

## 📋 Documentation

- [Requirements & User Stories](requirements.md) (original)
- [System Design & Architecture](design.md) (original)
- [Demo Script](docs/demo-script.md)

---

## 👥 Team CtrlZ

| Name | Role | Responsibilities |
|------|------|------------------|
| **Abel Mahesh Tharakan** | Product & Legal Lead | Documentation, testing, Team Coordination |
| **Shaury Tandon** | AI/ML Engineering | Claude Lambda, PDF generation |
| **Aditya Nair** | Cloud & Backend | AWS setup, Lambdas, API Gateway, Amplify |
| **Abhinav Mankar** | Frontend & UX | HTML/Tailwind UI, Cursor, recording |

---

## 🏆 Built for AWS AI for Bharat Hackathon

- ✅ Uses Generative AI on AWS (Bedrock + Claude 3)
- ✅ Built with Kiro for spec-driven development
- ✅ Serverless architecture (Lambda + S3 + API Gateway)
- ✅ Voice-first, Hindi-native design

---

## 📝 License

MIT

---

*Last updated: March 2026*
