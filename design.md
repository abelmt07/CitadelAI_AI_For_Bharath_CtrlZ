# Citadel AI: System Design Document
## Voice-First Legal Draft Generator for Bharat

### The Sub-2-Minute Engine

**Ramesh's Journey**: From Hindi voice complaint to court-ready Form I in under 2 minutes.

```mermaid
sequenceDiagram
    participant Ramesh
    participant App
    participant Transcribe
    participant NovaLite
    participant Validator
    participant Template
    
    Ramesh->>App: Hindi voice note
    App->>Transcribe: Convert to text
    Note over Transcribe: Fallback: Text input
    Transcribe-->>App: Text
    
    App->>NovaLite: Legal analysis + entity extraction
    Note over NovaLite: Amazon Nova Lite on Bedrock<br/>Extracts issue, company, amount, section
    NovaLite-->>App: Structured JSON data
    
    App->>Validator: Validate required fields
    Note over Validator: Invoice? Date within 2 years?<br/>Jurisdiction match?
    Validator-->>App: Missing evidence flags
    
    App->>Ramesh: Evidence checklist
    Ramesh->>App: Provides details
    
    App->>NovaLite: Generate Form I content
    NovaLite->>Template: Populate structured data
    Template-->>App: PDF draft
    App-->>Ramesh: Download ready
    
    Note over Ramesh,Template: Target: Sub-2-minutes
    ```

### Architectural Components

| Component | AWS Service | Purpose | Key Design Choice |
|-----------|-------------|---------|-------------------|
| **Voice Processor** | Amazon Transcribe | Hindi speech-to-text | Streaming transcription, confidence scoring |
| **Legal Brain** | **Amazon Nova Lite (Bedrock)** | Analyze complaints, extract entities, generate legal text | Cost-effective, fast inference for MVP |
| **Evidence Validator** | AWS Lambda | Rule-based validation before document generation | Invoice presence, 2-year limitation, jurisdiction match |
| **Document Generator** | Lambda + ReportLab | Generate court-compliant Form I PDFs | Template-based with legal validation |
| **API Layer** | Amazon API Gateway | Connect frontend to Lambda functions | CORS-enabled, IAM-secured endpoints |
| **Storage** | Amazon S3 | Store audio uploads and generated PDFs | Presigned URLs for secure downloads |
| **Frontend Hosting** | Vercel / AWS Amplify | Host HTML + Tailwind interface | CI/CD from GitHub, zero DevOps |
| **Security Layer** | AWS IAM | Manage access controls | Least privilege, service-specific roles |

*Note: Architecture simplified from original design.md to prioritize rapid development within the 5-day build window. Cohere Embed, Amazon Q, and DynamoDB were excluded in favor of direct Lambda calls and hardcoded legal knowledge for the MVP.*

### Data Flow: Privacy by Design

```mermaid
graph LR
    A["🎤 Voice Input"] --> B["🔒 API Gateway"]
    B --> C["📦 S3 Bucket<br/>Audio Upload"]
    C --> D["⚡ Transcribe Lambda<br/>Speech→Text"]
    D --> E["⚡ Nova Lite Lambda<br/>Legal Analysis + Entity Extraction"]
    E --> F["⚡ PDF Generator Lambda<br/>Form I Creation"]
    F --> G["📑 S3 PDF Storage"]
    G --> H["🔗 Presigned URL"]
    H --> I["📥 User Download"]
    
    style A fill:#0B6623,color:#fff
    style B fill:#2A6E6E,color:#fff
    style C fill:#4F7968,color:#fff
    style D fill:#0B6623,color:#fff
    style E fill:#2A6E6E,color:#fff
    style F fill:#4F7968,color:#fff
    style G fill:#0B6623,color:#fff
    style H fill:#2A6E6E,color:#fff
    style I fill:#4F7968,color:#fff```


---

**Data Lifecycle**:
- Voice: Deleted immediately post-transcription
- Transcript: Stored 24h for session continuity, then purged
- Form I draft: User-downloaded; 7-day retention for re-download only

### Scaling for Bharat

**From 1 to 1,000,000 Users with Serverless Architecture**

**Phase 1: Hackathon (1-100 users)**
- Single AWS region (Mumbai)
- Basic Lambda functions with 1024MB memory
- Manual monitoring
- **Vercel** frontend hosting

**Phase 2: Pilot (100-10,000 users)**
- Multi-AZ deployment for reliability
- Lambda provisioned concurrency for consistent performance
- CloudWatch automated monitoring
- DynamoDB (if session persistence needed)

**Phase 3: Scale (10,000-1,000,000 users)**
- Multi-region deployment (Mumbai, Singapore)
- API Gateway with caching and throttling
- Bedrock model endpoints with provisioned throughput
- Cost optimization: Lambda reserved concurrency

**Language Expansion (Post-Hackathon)**
- Q2 2026: Tamil (ta-IN), Telugu (te-IN), Malayalam (ml-IN), Marathi (mr-IN)
- Q3 2026: Gujarati, Kannada, Punjabi, Odia  
- Q4 2026: Bengali, Assamese, Urdu
- Architecture: Same Transcribe endpoint, different language-code parameter

### Hardest Technical Problems & Solutions

| Problem | Our Solution | Trade-off |
|---------|--------------|-----------|
| **Hindi speech accuracy varies by accent/region** | Transcribe hi-IN model + text input fallback | Simpler than multi-model ensemble |
| **Sub-2-Minute deadline with AI processing** | Single Nova Lite call handles both analysis + extraction | No parallel processing needed |
| **Evidence validation failures** | Rule-based checks + user re-prompt | Accuracy vs. user friction |
| **Legal accuracy cannot be compromised** | Template validation + hardcoded CPA sections | Limited scope but 100% reliable |
| **AWS costs could spiral** | Single Lambda per function, no orchestration overhead | Less flexible but cost-effective |

### Demo vs. Production

**Hackathon Submission (5-day build)**:
- ✅ Single user flow: Ramesh's telecom complaint
- ✅ Hardcoded CPA sections (Section 2(47), 2(9), etc.)
- ✅ Hindi transcription with fallback
- ✅ PDF generation with ReportLab
- ✅ Live URL on Vercel
- ✅ Demo video showing end-to-end flow

**Production System (3-6 months)**:
- 🚀 Multi-user concurrent processing
- 🚀 Dynamic legal template generation
- 🚀 WhatsApp integration for mass accessibility
- 🚀 Real-time legal database updates
- 🚀 Multi-language support (12 Indian languages)
- 🚀 Court e-filing API integration

**Technical Debt We Accept for Hackathon**:
- Hardcoded legal templates vs. dynamic generation
- No session persistence (in-memory only)
- Basic error handling vs. comprehensive recovery
- Manual testing vs. automated test suites

**Hackathon Constraints Acknowledged:**
- 5-day development window limits testing rigor
- AWS credits constrain scale testing
- Team of 4 requires focused MVP scope
- Demo prioritizes one perfect user journey (Ramesh's telecom case)

### Why This Architecture Wins

• **48-Hour Buildable** - Simplified serverless components snap together

• **Infinite Scale** - Auto-scaling from 1 to 1M users with Lambda + API Gateway

• **Cost Optimized** - ₹3-5 per request vs ₹5,000 lawyer fee

• **Privacy by Design** - Voice deleted immediately; transcripts expire in 24h

• **User-First** - Sub-2-Minute promise enforced in architecture

---

**The Bottom Line**: This isn't just a hackathon project—it's a production-ready architecture that can serve 1 million users while maintaining the sub-2-minute promise that makes justice accessible to Ramesh and millions like him across India. By simplifying the stack, we've made it **buildable in 5 days** and **scalable for the future**.

