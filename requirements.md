# Citadel AI: Voice-First Legal Draft Generator
## Hackathon Requirements Document

### The Problem: Justice Denied at Scale

**77% of Indians cannot access legal remedies** due to language barriers and cost constraints. With **50 million consumer complaints annually** and legal consultation fees starting at **₹5,000**, a ₹299 unauthorized charge becomes economically irrational to pursue.

**Bharat Context**: _**50 lakh+**_ consumer cases pending in District/State/National Commissions. Lawyer density in Tier 3 cities: **1 per 1400 people** vs. **1 per 300 in metros**.

**Meet Ramesh**: A shopkeeper in Lucknow facing unauthorized ₹299 monthly telecom deductions. His three options:
1. **Ignore it** → Lose ₹3,588 annually to corporate theft
2. **Hire lawyer** → Pay ₹5,000+ to recover ₹299 (net loss: ₹4,701)
3. **Navigate courts alone** → Face English legal documents, complex procedures, certain failure

**The Reality**: Complexity and cost create an access barrier that systematically favors corporations over consumers.

### Our Solution: First-Strike Legal Draft

**Core Innovation**: Bypasses legal complexity → delivers court-ready draft in a **Sub-2-min Journey**

**User Journey**: Voice Note → AI Transcription → Legal Analysis → Form I Generation → Ready to File

**Key Differentiator**: **We deliver a fileable legal instrument, not just advice.** Users get a complete "Form I" consumer complaint with proper legal grounds, not generic guidance.

### Target Users

**Primary**: Bharath native consumers in Tier 2/3 cities (pilot: Hindi-Speaking)
- Age: 25-60 years
- Profile: Limited English, basic smartphone use, WhatsApp-native
- Pain: Facing consumer disputes (telecom fraud, defective products, service failures)

**Secondary**: Consumer rights NGOs & legal aid clinics
- Use case: Scale assistance to underserved populations
- Impact: 10x more cases handled per legal worker

*Note: Pilot targets Hindi (hi-IN); architecture supports Tamil, Telugu, Malayalam, Marathi and 8+ additional languages via Amazon Transcribe language codes*

### Core Features & Technical Implementation

| Feature | User Experience | Technical Implementation | Success Metric |
|---------|----------------|-------------------------|----------------|
| **Voice-First Native Intake** | Records complaint in natural native speech | Amazon Transcribe + Hindi language model | >85% transcription accuracy |
| **AI Strategy Adviser** | Identifies issue type, suggests legal strategy | Claude 3 via Bedrock + Consumer Protection Act knowledge | >90% correct issue classification |
| **Evidence Validator** | Asks for specific proof (SMS, receipts, dates) | Rule-based validation: Invoice presence? Date within limitation period (2 years)? Jurisdiction match (District/State/National Commission based on claim value)? | 100% mandatory fields collected |
| **Plain-Language Law Guide** | Explains rights in conversational language | Cohere Embed + vector search + Claude 3 translation | User comprehension >4/5 rating |
| **Instant Legal Draft** | Generates complete Form I with legal grounds | Claude 3 + structured templates + PDF generation | 100% court-compliant format |

### Technical Architecture
```mermaid
graph LR
    A[Voice Input] --> B[Amazon Transcribe<br/>Speech→Text<br/><i>Hindi pilot</i>]
    B --> C[Bedrock<br/>Claude 3 Analysis]
    C --> D[Entity Extraction<br/>& Structuring Engine]
    C --> E[Cohere Embed<br/>Legal Knowledge Retrieval]
    D --> F[Evidence Validator<br/><i>Invoice? Date? Jurisdiction?</i>]
    E --> G[Amazon Q Business<br/>Orchestration]
    F --> G
    G --> H[Template Engine<br/>Form I Population]
    H --> I[PDF Generation]
    I --> J[User Download]
    
    style A fill:#0B6623,color:#fff
    style B fill:#4F7968,color:#fff
    style C fill:#2A6E6E,color:#fff
    style D fill:#2A6E6E,color:#fff,stroke:#fff,stroke-width:2px
    style E fill:#2A6E6E,color:#fff
    style F fill:#4F7968,color:#fff
    style G fill:#0B6623,color:#fff
    style H fill:#4F7968,color:#fff
    style I fill:#0B6623,color:#fff
    style J fill:#2A6E6E,color:#fff
```

**Key Technical Decisions**:
- **Serverless**: Zero infrastructure management, instant scaling
- **Privacy First**: Voice deleted immediately post-transcription; transcripts 24h TTL; drafts 7-day retention
- **Cost Optimized**: Pay-per-use, target <₹5 per draft at scale
- **AWS Native**: Transcribe, Bedrock (Claude 3 + Cohere), Lambda, Q Business

**AWS Services Stack**:
- **Amazon Transcribe**: Hindi speech-to-text
- **Amazon Bedrock**: Claude 3 (reasoning) + Cohere Embed (legal search)
- **Amazon Q Business**: Workflow orchestration
- **AWS Lambda**: Serverless compute
- **Amazon S3**: Document storage
- **Amazon DynamoDB**: Session management

### Success Metrics

**For Hackathon Demo**:
- ✅ **Target: Sub-2-minute journey** (validated against AWS service SLAs; subject to audio length and network conditions)
- ✅ **Complete Form I draft** with all mandatory fields
- ✅ **Hindi voice input** working with >85% accuracy
- ✅ **<₹5 cost per request** at scale

**For Scale Impact**:
- ✅ **1M+ users** supported on serverless architecture
- ✅ **₹5,000 saved per user** (avoided lawyer fees)
- ✅ **10x faster** than traditional legal consultation

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Indic Language ASR Accuracy <85%** | Core functionality fails | Amazon Transcribe hi-IN model; fallback to text input; extensible to 9+ languages via language code swap |
| **AWS costs exceed budget** | Demo becomes expensive | Usage caps, local testing, cached responses for common scenarios |
| **Legal formatting errors** | Invalid court documents | Template validation, Consumer Protection Act compliance checks, sample human review |

### MVP Scope & Future Roadmap

**What's NOT in Hackathon MVP**:
- Multiple Indian languages (Hindi only)
- Full case management (first draft only)
- Court filing integration (manual filing required)
- Legal representation (guidance only, clear disclaimers)

**Future Roadmap**:

- **Phase 1 (Now)**: Hindi pilot, WhatsApp integration, voice quality improvements
- **Phase 2 (Q2 2026)**: Tamil, Telugu, Malayalam, Marathi + defect tracking
- **Phase 3 (Q3 2026)**: Gujarati, Kannada, Punjabi, Odia + property disputes
- **Phase 4 (Q4 2026)**: Bengali, Assamese, Urdu + court e-filing integration


### Technical Constraints & Assumptions

**Hackathon Constraints**:
- **48-hour development window**
- **AWS free tier + $100 budget**
- **Team of 4 developers**
- **Stable demo for 15-minute presentation**

**Key Assumptions**:
- Amazon Transcribe Hindi accuracy sufficient for legal use
- Consumer Protection Act 2019 format remains stable
- Users have smartphone with microphone access
- Internet connectivity available for AWS services

### Legal & Ethical Considerations

- **Disclaimers**: Clear "guidance not legal advice" messaging throughout interface
- **Privacy**: Voice recordings deleted after processing, user data anonymized
- **Accuracy**: All legal citations verified against Consumer Protection Act 2019
- **Liability**: System provides document templates, users responsible for filing accuracy
- **Compliance**: Data stored in Indian AWS regions, GDPR-equivalent privacy protection

### Non-Functional Requirements

**Language Extensibility:**
- Architecture supports plug-and-play language models via Amazon Transcribe configuration
- Pilot: Hindi (hi-IN) validated against Lucknow dialect samples
- Roadmap: 12 Indian languages by Q4 2026
- Template engine supports multilingual Form I variants

**Data Lifecycle:**
- Voice: Deleted immediately post-transcription
- Transcript: Stored 24h for session continuity, then purged
- Form I draft: User-downloaded; 7-day retention for re-download only

---


**Bottom Line**: Citadel AI transforms the economics of consumer justice. Instead of choosing between ₹299 theft and ₹5,000 lawyer fees, Ramesh gets a court-ready legal draft in under **2 minutes** for <₹5. **This isn't legal tech—it's justice acceleration.**

