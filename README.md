# Citadel AI: Your First-Strike Legal Draft
## AI for Bharat Hackathon Project

**Voice to court-ready legal draft in 120 seconds for Hindi-speaking consumers**

### The Problem
77% of Indians cannot access legal remedies. ₹299 unauthorized charges become economically irrational to pursue, given ₹5,000+ in lawyer fees.

### Our Solution
AI-powered legal companion that turns Hindi voice notes about consumer issues into court-ready "Form I" drafts in **under 120 seconds**.

### Tech Stack (AWS Native)
- **Amazon Transcribe** - Hindi speech-to-text
- **Amazon Bedrock** - Claude 3 (legal reasoning) + Cohere Embed
- **Amazon Q Business** - Workflow orchestration
- **AWS Lambda + S3 + DynamoDB** - Serverless backend

### Key Features
1. **Voice-First Intake** - Speak naturally, no typing needed
2. **AI Strategy Adviser** - Identifies legal strategy automatically
3. **Evidence Validator** - Rule-based checklist for case strength
4. **Plain-Language Law Guide** - Consumer Protection Act explained simply
5. **Instant Legal Draft** - Court-ready Form I in 120 seconds

### Documentation
- [Requirements & User Stories](requirements.md)
- [System Design & Architecture](design.md)

### Team CtrlZ
- **Abel Mahesh Tharakan** - Product & Legal Lead
- **Shaury Tandon** - AIML Engineering
- **Aditya Nair** - Cloud & Backend
- **Abhinav Mankar** - Frontend & UX

---
*Built for AI for Bharat Hackathon powered by AWS. Proof of concept - not for actual legal use.*
