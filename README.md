# Citadel AI: Your First-Strike Legal Draft
### First-Strike Legal Draft Generator for Bharat

> **Transforming a Hindi voice complaint into a court-ready "Form I" in under 2 minutes.**

**The Problem**: 77% of Indians can't access legal remedies. A ₹299 fraud vs. a ₹5,000 lawyer fee = economic injustice.

**The Solution**: Voice-first AI that generates fileable consumer complaints. No lawyer required.

---

## How It Works

1. **Speak** — Hindi/English voice note
2. **Analyze** — Claude 3 extracts legal strategy  
3. **Validate** — Rule-based evidence checks
4. **Draft** — Court-compliant Form I PDF

**Target**: Sub-2-minute end-to-end journey.

---

### Tech Stack (AWS Native)
| Component | Service |
|-----------|---------|
| Voice → Text | Amazon Transcribe (hi-IN) |
| Legal Analysis | Amazon Bedrock (Claude 3) |
| Knowledge Retrieval | Cohere Embed |
| Entity Extraction | AWS Lambda |
| Orchestration | Amazon Q Business |
| Storage | DynamoDB + S3 |
| Security | IAM + KMS |

---

### Documentation
- [Requirements & User Stories](requirements.md)
- [System Design & Architecture](design.md)

---

### Team CtrlZ
- **Abel Mahesh Tharakan** - Product & Legal Lead
- **Shaury Tandon** - AI/ML Engineering
- **Aditya Nair** - Cloud & Backend
- **Abhinav Mankar** - Frontend & UX

---
*This repository contains documentation and design artifacts for the hackathon idea submission phase. Implementation to follow in subsequent rounds.*

