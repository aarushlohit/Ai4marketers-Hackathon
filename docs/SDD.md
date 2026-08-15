# Software Design Document (SDD)

## Miracle Birds — AI Intelligence Layer for CRM

**Document ID:** MB-SDD-001  
**Version:** 1.0  
**Date:** July 13, 2026  
**Status:** Approved  
**Classification:** Confidential

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Design](#2-architecture-design)
3. [Component Design](#3-component-design)
4. [Database Design](#4-database-design)
5. [API Design](#5-api-design)
6. [AI/ML Design](#6-aiml-design)
7. [Security Design](#7-security-design)
8. [Integration Design](#8-integration-design)
9. [Deployment Design](#9-deployment-design)
10. [Design Decisions & Trade-offs](#10-design-decisions--trade-offs)

---

## 1. System Overview

### 1.1 Purpose

This Software Design Document describes the architectural and detailed design of Miracle Birds — an enterprise AI Intelligence Layer that connects to CRM platforms and enhances them with AI-powered customer intelligence, predictive analytics, workflow automation, and an AI Copilot.

### 1.2 Design Principles

The system is designed according to the following architectural principles:

```
Clean Architecture       — Separation of concerns across layers
Domain-Driven Design     — Business logic expressed in domain language
SOLID Principles         — Single responsibility, Open/closed, etc.
Hexagonal Architecture   — Ports and adapters for external systems
Repository Pattern       — Abstracted data access
Service Layer Pattern    — Business logic in services
Dependency Injection     — Loose coupling between components
Event-Driven             — Async communication via events/queues
```

### 1.3 Technology Decisions Summary

| Component        | Technology               | Rationale                                   |
| ---------------- | ------------------------ | ------------------------------------------- |
| Backend API      | FastAPI (Python)         | Async-native, OpenAPI auto-gen, type-safe   |
| Frontend         | Next.js 14 (TypeScript)  | RSC, App Router, SEO, performance           |
| Database         | PostgreSQL 16 + pgvector | Vector search built-in, mature, ACID        |
| Cache            | Redis 7                  | Proven, versatile (cache + queue + pub/sub) |
| AI Orchestration | LangChain + LangGraph    | Ecosystem maturity, agent workflows         |
| ML Models        | XGBoost + scikit-learn   | Interpretable, fast inference, proven       |
| Async Tasks      | Celery + Redis           | Mature, distributed, monitoring support     |
| Containers       | Docker + Kubernetes      | Industry standard, cloud-native             |
| IaC              | Terraform                | Declarative, multi-cloud capable            |
| UI Components    | Shadcn UI (Radix)        | Accessible, customizable, no vendor lock-in |

---

## 2. Architecture Design

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│    Browser (Next.js 14 + React 18 + TypeScript)                 │
│    Mobile Browser  │  Third-party Integrations (API)            │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS / WebSocket
┌─────────────────────────▼───────────────────────────────────────┐
│                       API GATEWAY LAYER                          │
│    AWS ALB + NGINX Ingress + Rate Limiting + TLS Termination    │
└─────┬──────────┬──────────┬──────────┬──────────────────────────┘
      │          │          │          │
┌─────▼──┐ ┌────▼───┐ ┌────▼───┐ ┌────▼───────────────────────┐
│Backend │ │   AI   │ │   ML  │ │   CRM Integration          │
│  API   │ │Engine  │ │Engine │ │   Service                  │
│FastAPI │ │LangChain│ │XGBoost│ │   Adapters                 │
└────┬───┘ └────┬───┘ └────┬──┘ └────┬───────────────────────┘
     │          │           │         │
┌────▼──────────▼───────────▼─────────▼──────────────────────┐
│                     DATA LAYER                               │
│   PostgreSQL 16 (pgvector)  │  Redis 7  │  S3 (files)      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Microservices Topology

| Service         | Port | Responsibility                          | Scale     |
| --------------- | ---- | --------------------------------------- | --------- |
| Backend API     | 8000 | Core REST API, auth, business logic     | 3–10 pods |
| AI Engine       | 8001 | LLM orchestration, copilot, embeddings  | 2–6 pods  |
| ML Engine       | 8002 | Predictive models, scoring, forecasting | 2–5 pods  |
| CRM Integration | 8003 | OAuth, sync, webhook processing         | 2–4 pods  |
| Security Engine | 8004 | Prompt firewall, PII detection          | 2–4 pods  |
| Frontend        | 3000 | Next.js SSR/SSG web app                 | 2–8 pods  |
| Celery Workers  | —    | Background async jobs                   | 2–8 pods  |

### 2.3 Clean Architecture Layers (Backend)

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│   FastAPI Routers, Pydantic Schemas     │
│   HTTP request/response handling        │
├─────────────────────────────────────────┤
│           Application Layer             │
│   Use Cases, Application Services       │
│   Orchestrates domain objects           │
├─────────────────────────────────────────┤
│             Domain Layer                │
│   Entities, Value Objects, Events       │
│   Pure business logic, no I/O           │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │
│   Repositories (SQLAlchemy)             │
│   External API clients, Redis, S3       │
└─────────────────────────────────────────┘
```

---

## 3. Component Design

### 3.1 Backend API Service

#### Directory Structure

```
apps/backend/
├── main.py                    # FastAPI app entry point
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── router.py      # Aggregates all endpoint routers
│   │       ├── dependencies.py # Shared DI: auth, pagination, DB session
│   │       └── endpoints/
│   │           ├── auth.py        # /api/v1/auth/*
│   │           ├── customers.py   # /api/v1/customers/*
│   │           ├── predictions.py # /api/v1/predictions/*
│   │           ├── analytics.py   # /api/v1/analytics/*
│   │           ├── integrations.py # /api/v1/integrations/*
│   │           ├── users.py       # /api/v1/users/*
│   │           └── workflows.py   # /api/v1/workflows/*
│   ├── core/
│   │   ├── config.py          # Pydantic Settings (env vars)
│   │   ├── database.py        # SQLAlchemy engine, session, RLS
│   │   ├── security.py        # JWT creation/validation, bcrypt
│   │   └── celery_app.py      # Celery configuration
│   ├── domain/
│   │   ├── entities/          # Customer, User, Prediction
│   │   ├── value_objects/     # Email, ChurnScore, LeadScore
│   │   └── events/            # CustomerCreated, PredictionCompleted
│   ├── use_cases/
│   │   ├── auth/              # LoginUseCase, RegisterUseCase
│   │   ├── customer/          # GetCustomer360UseCase
│   │   └── prediction/        # RunChurnPredictionUseCase
│   ├── services/              # CustomerService, PredictionService
│   ├── repositories/          # CustomerRepository, UserRepository
│   ├── models/                # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic request/response schemas
│   └── middleware/
│       ├── tenant.py          # Multi-tenant context
│       ├── logging.py         # Structured JSON logging
│       └── rate_limit.py      # Redis-backed rate limiting
```

#### Key Design Patterns

**Repository Pattern:**

```python
class CustomerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: UUID) -> Customer | None:
        result = await self.db.execute(
            select(CustomerModel).where(CustomerModel.id == id)
        )
        return result.scalar_one_or_none()

    async def list_paginated(
        self, tenant_id: UUID, page: int, page_size: int, filters: dict
    ) -> tuple[list[Customer], int]:
        # ... paginated query with RLS active via session
```

**Use Case Pattern:**

```python
class GetCustomer360UseCase:
    def __init__(
        self,
        customer_repo: CustomerRepository,
        prediction_service: PredictionService,
        interaction_repo: InteractionRepository,
    ):
        self.customer_repo = customer_repo
        self.prediction_service = prediction_service
        self.interaction_repo = interaction_repo

    async def execute(self, customer_id: UUID) -> Customer360:
        customer = await self.customer_repo.get_by_id(customer_id)
        predictions = await self.prediction_service.get_all(customer_id)
        interactions = await self.interaction_repo.get_recent(customer_id, limit=10)
        return Customer360(customer=customer, predictions=predictions, ...)
```

### 3.2 AI Engine Service

#### Agents

| Agent                    | Purpose                           | LLM             | Tools                        |
| ------------------------ | --------------------------------- | --------------- | ---------------------------- |
| CRMCopilotAgent          | Answer questions about CRM data   | GPT-4-turbo     | DB query, customer lookup    |
| ExecutiveCopilotAgent    | Generate business summaries       | GPT-4-turbo     | Analytics API, report gen    |
| MeetingIntelligenceAgent | Transcribe and summarize meetings | Whisper + GPT-4 | Audio transcription          |
| NextBestActionAgent      | Recommend customer actions        | GPT-4-turbo     | Prediction API, rules engine |

#### LangGraph Agent Flow

```
User Message
     │
     ▼
[Input Validation + PII Scrub]
     │
     ▼
[Security Firewall — Prompt Injection Check]
     │
     ▼
[Router Node — classify intent]
     │
  ┌──┴──────────┬─────────────┐
  ▼             ▼             ▼
[Customer    [Analytics   [Action
  Lookup]      Query]    Recommender]
  │             │             │
  └──────────┬──┘             │
             ▼                │
      [Response Synthesis]◄───┘
             │
             ▼
      [PII Output Scan]
             │
             ▼
      [Response to User]
```

### 3.3 ML Engine Service

#### Model Architecture

```
Customer Data
      │
      ▼
[Feature Engineering Pipeline]
  ├── Behavioral features (usage, login frequency)
  ├── Transactional features (revenue, orders)
  ├── Support features (tickets, CSAT)
  ├── Engagement features (email, meetings)
  └── Temporal features (trends, seasonality)
      │
      ▼
[Model Inference]
  ├── Churn Model (XGBoost)        → churn_probability
  ├── Lead Score Model (RF)        → lead_score
  ├── Revenue Model (GBT + ARIMA)  → revenue_forecast
  └── Health Score (Ensemble)      → health_score
      │
      ▼
[SHAP Explainability]
  └── Top 5 feature importances per prediction
      │
      ▼
[Store Results to PostgreSQL]
```

### 3.4 Frontend Architecture

#### Next.js App Router Structure

```
src/app/
├── (auth)/                  # Auth route group — no sidebar
│   ├── login/page.tsx       # Login page (Server Component)
│   ├── register/page.tsx    # Register page
│   └── callback/page.tsx    # OAuth callback handler
│
└── (dashboard)/             # Dashboard route group — with sidebar
    ├── layout.tsx           # Dashboard shell (sidebar + topnav)
    ├── overview/page.tsx    # Home dashboard
    ├── customers/
    │   ├── page.tsx         # Customer list
    │   └── [id]/page.tsx    # Customer detail / 360 view
    ├── predictions/page.tsx # Predictions overview
    ├── analytics/page.tsx   # Analytics & charts
    ├── copilot/page.tsx     # AI Copilot chat UI
    ├── integrations/page.tsx # CRM connections
    ├── settings/page.tsx    # User & org settings
    └── workflows/page.tsx   # Workflow automation
```

#### State Management Strategy

```
Server State  → TanStack Query (React Query)
  - Customer list, predictions, analytics
  - Auto-cache, background refresh, optimistic updates

Client State  → Zustand
  - Auth tokens, user profile, UI preferences
  - Sidebar open/closed, selected theme

Form State    → React Hook Form + Zod
  - All forms with schema validation
  - Error messages derived from Zod schema

URL State     → Next.js searchParams
  - Filters, pagination, active tab
```

---

## 4. Database Design

### 4.1 Schema Organization

All tables are organized into PostgreSQL schemas for logical separation:

| Schema         | Purpose              | Key Tables                                    |
| -------------- | -------------------- | --------------------------------------------- |
| `core`         | Tenants, users, RBAC | tenants, users, roles, permissions            |
| `customers`    | CRM data             | customers, interactions, segments             |
| `predictions`  | ML outputs           | churn_predictions, lead_scores, health_scores |
| `integrations` | CRM connections      | crm_connections, sync_jobs, webhook_events    |
| `ai`           | Copilot data         | conversations, messages, embeddings           |
| `workflows`    | Automation           | workflow_definitions, workflow_executions     |
| `analytics`    | Metrics              | customer_metrics, aggregated_stats            |
| `security`     | Audit & events       | audit_logs, security_events, pii_detections   |

### 4.2 Multi-Tenancy via Row-Level Security

Every customer-facing table includes `tenant_id`. PostgreSQL RLS policies enforce isolation:

```sql
-- RLS policy on customers table
ALTER TABLE customers.customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON customers.customers
    USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

The application sets `app.tenant_id` at the start of each request via middleware, so no application-level tenant filtering is required — the database enforces it.

### 4.3 Vector Search (pgvector)

Customer interaction embeddings are stored as `vector(1536)` (OpenAI ada-002 dimensions):

```sql
CREATE TABLE ai.embeddings (
    id          UUID PRIMARY KEY,
    tenant_id   UUID NOT NULL,
    source_type TEXT NOT NULL,  -- 'interaction', 'document', 'note'
    source_id   UUID NOT NULL,
    embedding   vector(1536) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for approximate nearest neighbor search
CREATE INDEX ON ai.embeddings USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

Similarity search query:

```sql
SELECT source_id, 1 - (embedding <=> $1) AS similarity
FROM ai.embeddings
WHERE tenant_id = $2
ORDER BY embedding <=> $1
LIMIT 10;
```

---

## 5. API Design

### 5.1 Design Principles

- **RESTful:** Resource-based URLs, standard HTTP verbs
- **Versioned:** All endpoints under `/api/v1/` prefix
- **Consistent responses:** Uniform envelope for lists (`{ items, total, page }`)
- **Error format:** `{ error, detail, code }` on all 4xx/5xx
- **Pagination:** Cursor-based for large datasets, offset for smaller
- **Rate limiting:** Per-tenant via Redis token bucket

### 5.2 Authentication Flow

```
POST /api/v1/auth/login
  → Verify credentials
  → Generate access_token (HS256 JWT, 30 min)
  → Generate refresh_token (HS256 JWT, 7 days)
  → Return both tokens

Subsequent requests:
  Authorization: Bearer <access_token>
  → Middleware decodes JWT
  → Sets request.state.user + request.state.tenant_id
  → Sets PostgreSQL RLS context

Token refresh:
  POST /api/v1/auth/refresh  { refresh_token }
  → Validate refresh token (not expired, not revoked)
  → Issue new access_token (+ rotate refresh_token)
```

### 5.3 Request Lifecycle

```
HTTP Request
     │
     ▼
[TenantMiddleware]        — Extract tenant from JWT, set RLS
     │
     ▼
[LoggingMiddleware]       — Structured request log
     │
     ▼
[RateLimitMiddleware]     — Redis token bucket check
     │
     ▼
[Auth Dependency]         — Validate JWT, inject User
     │
     ▼
[Route Handler]           — Call use case / service
     │
     ▼
[Response Serialization]  — Pydantic model → JSON
     │
     ▼
HTTP Response (with X-Request-ID, X-RateLimit-* headers)
```

---

## 6. AI/ML Design

### 6.1 LLM Integration

Miracle Birds uses a **model-agnostic** architecture. The same agent can use OpenAI GPT-4 or Google Gemini by swapping the LLM provider:

```python
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm(provider: str = "openai"):
    if provider == "openai":
        return ChatOpenAI(model="gpt-4-turbo", temperature=0)
    elif provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0)
```

### 6.2 Retrieval Augmented Generation (RAG)

The AI Copilot uses RAG to ground answers in actual customer data:

```
User: "What's the risk level for Acme Corp?"
        │
        ▼
[Embed query with text-embedding-ada-002]
        │
        ▼
[Vector search against ai.embeddings]
  → Retrieve top-10 relevant interactions, notes, documents
        │
        ▼
[Build context window]
  System prompt + retrieved docs + user query
        │
        ▼
[LLM generates grounded answer]
        │
        ▼
[PII scan on output]
        │
        ▼
Response to user
```

### 6.3 Prompt Engineering

All prompts follow a structured template:

```
SYSTEM: You are an AI assistant for {company_name}'s CRM intelligence platform.
        You have access to customer data within {tenant_name}'s account.

        Rules:
        - Only answer questions about {tenant_name}'s data
        - Never reveal data from other organizations
        - If you don't know, say so — do not hallucinate
        - Keep responses concise and actionable

CONTEXT: {retrieved_customer_data}

CONVERSATION: {chat_history}

USER: {user_message}
```

### 6.4 ML Model Lifecycle

```
1. Data Collection    → Pull from PostgreSQL (feature store)
2. Feature Engineering → 50+ computed features per customer
3. Model Training      → XGBoost/RF with cross-validation
4. Experiment Tracking → MLflow (metrics, params, artifacts)
5. Model Evaluation    → AUC-ROC, F1, MAPE, hold-out test set
6. Model Registration  → MLflow model registry (staging → prod)
7. Deployment          → FastAPI inference endpoint
8. Monitoring          → Prediction distribution, data drift
9. Retraining Trigger  → Weekly cron OR on drift detection
```

---

## 7. Security Design

### 7.1 Defense in Depth

```
Layer 1: Network      — VPC, Security Groups, WAF, DDoS protection
Layer 2: Perimeter    — API Gateway, rate limiting, IP allowlisting
Layer 3: Application  — Input validation, OWASP controls, CSP headers
Layer 4: AI Security  — Prompt firewall, PII scrubbing, content filter
Layer 5: Auth/Authz   — JWT + RBAC + MFA + session management
Layer 6: Data         — Encryption at rest + in transit, column-level
Layer 7: Monitoring   — SIEM, anomaly detection, audit logging
```

### 7.2 Prompt Injection Firewall

All user inputs to the AI system pass through a two-stage firewall:

```python
class PromptFirewall:
    def scan(self, prompt: str) -> ScanResult:
        # Stage 1: Pattern-based detection (fast, < 5ms)
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return ScanResult(blocked=True, reason="pattern_match")

        # Stage 2: ML classifier (slower, ~50ms, for subtle injections)
        score = self.classifier.predict(prompt)
        if score > 0.85:
            return ScanResult(blocked=True, reason="ml_classifier")

        return ScanResult(blocked=False)
```

### 7.3 Secrets Management

No secrets are stored in environment variables in production. All secrets live in AWS Secrets Manager and are loaded at startup:

```python
import boto3

def load_secrets():
    client = boto3.client("secretsmanager", region_name="us-east-1")
    secret = client.get_secret_value(SecretId="miracle-birds/production/app")
    return json.loads(secret["SecretString"])
```

---

## 8. Integration Design

### 8.1 Adapter Pattern

Each CRM integration implements the same `CRMAdapter` interface:

```python
class CRMAdapter(ABC):
    @abstractmethod
    async def authenticate(self) -> bool: ...
    @abstractmethod
    async def get_contacts(self, filters, limit) -> list[dict]: ...
    @abstractmethod
    async def create_contact(self, data) -> dict: ...
    @abstractmethod
    async def update_contact(self, id, data) -> dict: ...
    @abstractmethod
    def map_to_unified(self, crm_data) -> UnifiedCustomer: ...
    @abstractmethod
    def map_from_unified(self, unified) -> dict: ...
```

Adding a new CRM (e.g., Freshsales) only requires implementing this interface — no changes to the sync engine, webhook processor, or API layer.

### 8.2 Sync Architecture

```
Full Sync (initial):
  Celery task → paginate CRM API (100 records/page)
              → transform each page to unified schema
              → bulk upsert into PostgreSQL
              → trigger ML predictions for new customers
              → update sync job status

Incremental Sync (hourly):
  Celery beat → fetch records modified since last_sync_at
              → same transform + upsert flow
              → much faster (typically < 500 records/run)

Real-time Sync (webhooks):
  POST /webhooks/{crm_type}
              → verify HMAC signature
              → log raw event
              → enqueue Celery task
              → task fetches full record + applies update
```

---

## 9. Deployment Design

### 9.1 Environment Strategy

| Environment | Branch  | Auto-deploy         | Purpose                 |
| ----------- | ------- | ------------------- | ----------------------- |
| Development | local   | No                  | Developer local testing |
| Staging     | develop | Yes                 | QA, integration testing |
| Production  | main    | Yes (with approval) | Live system             |

### 9.2 Zero-Downtime Deployment

Kubernetes rolling updates with:

- `maxUnavailable: 0` — never remove a pod before a new one is ready
- `maxSurge: 1` — spin up one extra pod during rollout
- Readiness probes before traffic is routed to new pods
- Automatic rollback if rollout fails health checks

### 9.3 Configuration Hierarchy

```
Base config (committed to git):
  infrastructure/kubernetes/base/

Environment overlays (committed, secrets redacted):
  infrastructure/kubernetes/overlays/production/
  infrastructure/kubernetes/overlays/staging/

Secrets (never committed — injected via AWS Secrets Manager):
  DATABASE_URL, REDIS_URL, JWT_SECRET, API_KEYS
```

---

## 10. Design Decisions & Trade-offs

| Decision          | Chosen                   | Rejected                | Reason                                                          |
| ----------------- | ------------------------ | ----------------------- | --------------------------------------------------------------- |
| Backend framework | FastAPI                  | Django REST, Flask      | Async-native, fastest Python framework, auto OpenAPI            |
| DB multi-tenancy  | Row-Level Security       | Separate DBs per tenant | Lower cost, simpler ops; acceptable isolation for SaaS          |
| Frontend routing  | Next.js App Router       | Pages Router            | RSC support, nested layouts, better performance                 |
| ML model type     | XGBoost                  | Deep Learning (LSTM)    | More interpretable, faster inference, less data required        |
| State management  | Zustand + TanStack Query | Redux                   | Less boilerplate; TanStack Query purpose-built for server state |
| UI library        | Shadcn (Radix)           | Material UI, Ant Design | No vendor lock-in, fully customizable, accessible               |
| Auth tokens       | JWT (stateless)          | Session cookies         | Better for microservices and mobile clients                     |
| Message queue     | Redis (Celery)           | RabbitMQ, Kafka         | Simpler ops; Redis already in stack for caching                 |
| IaC               | Terraform                | AWS CDK, Pulumi         | Most mature, largest community, provider-agnostic               |
| Vector DB         | pgvector (PostgreSQL)    | Pinecone, Weaviate      | One fewer service; pgvector sufficient at this scale            |

---

**Document Version:** 1.0  
**Approved By:** Engineering Lead  
**Date:** July 13, 2026  
**Next Review:** January 13, 2027
