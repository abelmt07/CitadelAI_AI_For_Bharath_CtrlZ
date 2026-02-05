# Citadel AI: System Design Document
## Voice-First Legal Draft Generator for Bharat

### The Sub-2-Minute Engine

**Ramesh's Journey**: From Hindi voice complaint to court-ready Form I in under 2 minutes.

```mermaid
sequenceDiagram
    participant Ramesh
    participant App
    participant Transcribe
    participant Claude3
    participant EntityExtractor
    participant EvidenceValidator
    participant Cohere
    participant Template
    
    Ramesh->>App: Hindi voice note
    App->>Transcribe: Convert to text
    Note over Transcribe: Fallback: Text input
    Transcribe-->>App: Text
    
    App->>Claude3: Legal analysis
    Note over Claude3: Fallback: Cached responses
    Claude3->>Cohere: Retrieve relevant CPA sections
    Cohere-->>Claude3: Vector search results (top-k=3)
    Claude3->>Claude3: Synthesize with complaint context
    Claude3-->>App: Legal strategy (unstructured)
    
    App->>EntityExtractor: Extract Form I fields
    Note over EntityExtractor: Regex + few-shot prompting<br/>Complainant, Opposite Party,<br/>Relief Sought, Jurisdiction
    EntityExtractor-->>App: Structured data
    
    App->>EvidenceValidator: Validate required fields
    Note over EvidenceValidator: Invoice? Date? Jurisdiction?
    EvidenceValidator-->>App: Missing evidence flags
    
    App->>Ramesh: Evidence checklist
    Ramesh->>App: Provides details
    
    App->>Claude3: Generate Form I content
    Claude3->>Template: Populate structured data
    Template-->>App: PDF draft
    App-->>Ramesh: Download ready
    
    Note over Ramesh,Template: Target: Sub-2-minutes
```

### Architectural Components

| Component | AWS Service | Purpose | Key Design Choice |
|-----------|-------------|---------|-------------------|
| **Voice Processor** | Amazon Transcribe | Hindi speech-to-text with legal domain optimization | Streaming transcription for real-time feedback, confidence scoring |
| **Legal Brain** | Claude 3 (Bedrock) | Analyze complaints, identify legal issues, generate documents | Large context window for Consumer Protection Act knowledge |
| **Entity Extractor** | AWS Lambda | Convert unstructured Claude output to structured Form I fields | Regex + few-shot prompting for field mapping |
| **Knowledge Engine** | Cohere Embed | Vector search across legal documents in Hindi/English | Multilingual embeddings for cross-language legal retrieval |
| **Workflow Orchestrator** | Amazon Q Business | Coordinate Sub-2-Minute pipeline with conversational state | Stateful AI orchestration vs. rigid state machines |
| **Evidence Validator** | AWS Lambda | Rule-based validation before document generation | Invoice presence, 2-year limitation, jurisdiction match |
| **Document Generator** | Lambda + ReportLab | Generate court-compliant Form I PDFs | Template-based with legal validation |
| **Session Manager** | DynamoDB | Track user progress, temporary data storage | NoSQL for flexible schema, auto-expiring records |
| **Security Layer** | IAM + KMS | Encrypt voice data, manage access controls | Least privilege, automatic key rotation |

### Data Flow: Privacy by Design

```mermaid
graph LR
    A["🎤 Voice Input"] --> B["🔒 Encrypted HTTPS"]
    B --> C["💾 Voice Buffer<br/>Immediate Delete"]
    C --> D["🗣️ Transcribe"]
    D --> E["🧠 Claude 3<br/>Legal Analysis"]
    E --> F["📊 Entity Extractor<br/>Structure Data"]
    F --> G["✅ Evidence Validator"]
    G --> H["📄 Template Engine"]
    H --> I["📑 Form I PDF"]
    I --> J["📥 User Download"]
    J --> K["🗑️ Auto-delete<br/>Transcript<br/>24h TTL"]
    
    style A fill:#0B6623,color:#fff
    style B fill:#2A6E6E,color:#fff
    style C fill:#4F7968,color:#fff
    style D fill:#0B6623,color:#fff
    style E fill:#2A6E6E,color:#fff
    style F fill:#2A6E6E,color:#fff,stroke:#fff,stroke-width:2px
    style G fill:#4F7968,color:#fff
    style H fill:#4F7968,color:#fff
    style I fill:#0B6623,color:#fff
    style J fill:#2A6E6E,color:#fff
    style K fill:#4F7968,color:#fff
```

### Scaling for Bharat

**From 1 to 1,000,000 Users with Serverless Architecture**

**Phase 1: Hackathon (1-100 users)**
- Single AWS region (Mumbai)
- Basic Lambda functions with 3GB memory
- DynamoDB on-demand pricing
- Manual monitoring

**Phase 2: Pilot (100-10,000 users)**
- Multi-AZ deployment for reliability
- Lambda provisioned concurrency for consistent performance
- DynamoDB auto-scaling with read replicas
- CloudWatch automated monitoring

**Phase 3: Scale (10,000-1,000,000 users)**
- Multi-region deployment (Mumbai, Singapore, Frankfurt)
- API Gateway with caching and throttling
- Bedrock model endpoints with reserved capacity
- ElastiCache for legal template caching
- Cost optimization: Spot instances for batch processing

**Language Expansion (Post-Hackathon)**
- Q2 2026: Tamil (ta-IN), Telugu (te-IN), Malayalam (ml-IN), Marathi (mr-IN)
- Q3 2026: Gujarati, Kannada, Punjabi, Odia  
- Q4 2026: Bengali, Assamese, Urdu
- Architecture: Same Transcribe endpoint, different language-code parameter

### Hardest Technical Problems & Solutions

| Problem | Our Solution | Trade-off |
|---------|--------------|-----------|
| **Hindi speech accuracy varies by accent/region** | Multi-model ensemble: Transcribe + Whisper fallback, confidence scoring, text input option | Higher cost for dual transcription vs. user experience |
| **Sub-2-Minute deadline with complex AI processing** | Parallel processing: Transcription + legal analysis simultaneously, cached legal knowledge | Memory usage vs. speed optimization |
| **Evidence Validation Fails** | Rule-based checks (Invoice, Date, Jurisdiction) + user re-prompt via Amazon Q | Accuracy vs. user friction |
| **Legal accuracy cannot be compromised** | Template validation: Pre-verified Form I templates, Claude 3 fact-checking, human review samples | Development time vs. legal liability risk |
| **AWS costs could spiral with AI usage** | Smart caching: Common legal explanations cached, request batching, usage caps per user | Feature richness vs. cost control |
| **Consumer Protection Act complexity** | Focused scope: Start with telecom/e-commerce only, expand gradually | Market coverage vs. technical feasibility |

### Demo vs. Production

**Hackathon Demo (48 hours)**:
- ✅ Single user flow: Ramesh's telecom complaint
- ✅ Pre-loaded legal templates for common issues
- ✅ Basic Hindi transcription with fallback
- ✅ Simple PDF generation with manual formatting
- ✅ Local testing with mock AWS responses

**Production System (3-6 months)**:
- 🚀 Multi-user concurrent processing
- 🚀 Dynamic legal template generation
- 🚀 Advanced NLP for complex complaint analysis
- 🚀 WhatsApp integration for mass accessibility
- 🚀 Real-time legal database updates
- 🚀 Multi-language support

**Technical Debt We Accept for Hackathon**:
- Hardcoded legal templates vs. dynamic generation
- Single-threaded processing vs. parallel pipelines
- Basic error handling vs. comprehensive recovery
- Manual testing vs. automated test suites

**Hackathon Constraints Acknowledged:**
- 48-hour development window limits testing rigor
- AWS credits constrain scale testing
- Team of 4 requires focused MVP scope
- Demo prioritizes one perfect user journey (Ramesh's telecom case)

### Why This Architecture Wins

• **48-Hour Buildable** - Serverless components snap together

• **Infinite Scale** - Auto-scaling from 1 to 1M users  

• **Cost Optimized** - ₹3-5 per request vs ₹5,000 lawyer fee

• **Privacy by Design** - No permanent voice storage

• **User-First** - Sub-2-Minute promise enforced in architecture

---


**The Bottom Line**: This isn't just a hackathon project—it's a production-ready architecture that can serve 1 million users while maintaining the 120-second promise that makes justice accessible to Ramesh and millions like him across India.
