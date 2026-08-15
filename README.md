# 🐦 Miracle Birds

**The Secure AI Intelligence Layer for Every CRM**

Miracle Birds is NOT another CRM. It connects to your existing CRM (Salesforce, Zoho, HubSpot, Dynamics 365, Pipedrive) and adds a layer of AI-powered intelligence on top — giving your team predictive insights, automated workflows, and a conversational AI Copilot.

---

## What It Does

| Feature                   | Description                                            |
| ------------------------- | ------------------------------------------------------ |
| **AI CRM Copilot**        | Ask natural language questions about your customers    |
| **Churn Prediction**      | XGBoost model — AUC-ROC > 0.85                         |
| **Lead Scoring**          | 0–100 score with explainable factors                   |
| **Revenue Forecasting**   | 30/60/90-day forecasts per customer                    |
| **Customer Health Score** | Composite score from 5 dimensions                      |
| **Next Best Action**      | AI-recommended actions per customer                    |
| **Workflow Automation**   | Trigger emails/tasks when predictions cross thresholds |
| **CRM Integration**       | Bi-directional sync, real-time webhooks, OAuth 2.0     |

---

## Quick Start (Local Development)

### Prerequisites

- Docker Desktop 4.x+
- Node.js 20+
- Python 3.11+

### Run Everything

```bash
# 1. Clone
git clone https://github.com/your-org/miracle-birds.git
cd miracle-birds

# 2. Configure environment
cp .env.example .env
# Edit .env — add your OpenAI key and CRM OAuth credentials

# 3. Start all services
docker compose up --build

# 4. Open the app
#    Frontend:  http://localhost:3000
#    API Docs:  http://localhost:8000/docs
#    MLflow:    http://localhost:5000
#    Grafana:   http://localhost:3001  (admin/admin)
```

### Run Services Individually

```bash
# Backend API
cd apps/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd apps/frontend
npm install
npm run dev

# AI Engine
cd apps/ai-engine
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# ML Engine
cd apps/ml-engine
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

---

## Architecture

```
Browser
  │
  ▼
Next.js 14 (Frontend)
  │
  ▼
FastAPI (Backend API :8000)  ─── PostgreSQL 16 + pgvector
  │                               Redis 7
  ├── AI Engine    :8001  ──── OpenAI GPT-4 / Gemini
  ├── ML Engine    :8002  ──── XGBoost / scikit-learn
  ├── CRM Service  :8003  ──── Salesforce / Zoho / HubSpot / Dynamics / Pipedrive
  └── Security     :8004  ──── Prompt Firewall / PII Detection
```

---

## Technology Stack

### Backend

`FastAPI` · `SQLAlchemy 2.0 async` · `Pydantic v2` · `Celery + Redis` · `Alembic` · `bcrypt + JWT`

### AI / ML

`LangChain` · `LangGraph` · `OpenAI GPT-4-turbo` · `Google Gemini Pro` · `XGBoost` · `scikit-learn` · `SHAP` · `MLflow` · `pgvector`

### Frontend

`Next.js 14` · `TypeScript` · `Tailwind CSS` · `Shadcn UI` · `TanStack Query` · `Zustand` · `React Hook Form + Zod` · `Axios`

### Infrastructure

`Docker` · `Kubernetes (EKS)` · `Terraform` · `Prometheus` · `Grafana` · `GitHub Actions`

---

## Project Structure

See [FOLDER_STRUCTURE.md](./FOLDER_STRUCTURE.md) for the full directory tree.

## Documentation

| Document                                                          | Description                         |
| ----------------------------------------------------------------- | ----------------------------------- |
| [Technical Blueprint](./docs/TECHNICAL_BLUEPRINT.md)              | Master project index                |
| [SRS](./docs/SRS.md)                                              | Software Requirements Specification |
| [SDD](./docs/SDD.md)                                              | Software Design Document            |
| [API Docs](./docs/api/API_DOCUMENTATION.md)                       | REST API reference                  |
| [OpenAPI Spec](./docs/api/openapi.yaml)                           | OAS 3.0 machine-readable spec       |
| [System Architecture](./docs/architecture/SYSTEM_ARCHITECTURE.md) | Architecture diagrams               |
| [Database Schema](./docs/database/DATABASE_SCHEMA.md)             | ER diagrams, table definitions      |
| [Security Architecture](./docs/security/SECURITY_ARCHITECTURE.md) | Security design                     |
| [Deployment Guide](./docs/deployment/DEPLOYMENT_GUIDE.md)         | AWS + Kubernetes runbook            |

---

## CRM Integration

Miracle Birds connects to 5 CRM platforms via OAuth 2.0:

| CRM                    | API          | Sync                          |
| ---------------------- | ------------ | ----------------------------- |
| Salesforce             | REST v58.0   | Full + Incremental + Webhooks |
| Zoho CRM               | v3           | Full + Incremental + Webhooks |
| HubSpot                | v3           | Full + Incremental + Webhooks |
| Microsoft Dynamics 365 | Web API v9.2 | Full + Incremental            |
| Pipedrive              | v1           | Full + Incremental + Webhooks |

---

## Security & Compliance

- 🔒 **Prompt Injection Firewall** — pattern + ML detection
- 🔍 **PII Detection & Masking** — email, phone, SSN, credit cards
- 🛡️ **7-layer defense in depth**
- ✅ **GDPR**, **SOC 2 Type II**, **HIPAA**, **CCPA** compliant
- 🔐 **JWT + RBAC + MFA** authentication
- 📝 **Immutable audit logs** (90-day retention)

---

## Performance Targets

| Metric                | Target      |
| --------------------- | ----------- |
| API P95 response time | < 200ms     |
| ML prediction latency | < 2 seconds |
| AI Copilot response   | < 5 seconds |
| System uptime         | 99.9% SLA   |
| Concurrent users      | 10,000+     |

---

## License

Proprietary — © 2026 Miracle Birds. All rights reserved.
