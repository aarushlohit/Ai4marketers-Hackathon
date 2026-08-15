# Miracle Birds - Phase 1 (Hackathon MVP)

## Software Design Document (SDD) & Technical Blueprint

### 1. Objective

The objective of Phase 1 is to build a production-ready Hackathon MVP for **Miracle Birds**, the AI Intelligence Layer designed specifically for Frappe CRM. Miracle Birds transforms raw CRM data (Leads, Contacts, Organizations, Deals) into predictive insights and actionable intelligence using Machine Learning and Large Language Models, without replacing the core CRM system.

### 2. Scope

The scope of Phase 1 focuses exclusively on demonstrating the core intelligence capabilities.
**In Scope:**

- Integration with Frappe CRM via REST API.
- Customer 360 Dashboard with AI Summary.
- Executive Dashboard with Next Best Action Engine.
- AI CRM Copilot (Natural Language Chat).
- Explainable ML predictions (Mocked endpoints for MVP demonstration).
- Basic JWT Authentication layer.

**Out of Scope:**

- Bidirectional real-time CRM sync (Webhooks & complete database synchronization).
- Fully trained custom LLMs (using OpenAI/Gemini instead).
- Workflow automation (email dispatching, automated tasks).

### 3. Features

1. **Frappe CRM Integration:** Real-time fetching of Leads, Organizations, and Deals using the Frappe CRM REST API framework.
2. **Customer 360 Dashboard:** A unified view summarizing the customer timeline, deal history, AI summary, and health score.
3. **AI CRM Copilot:** Natural language interface for salespeople to query CRM data intuitively (e.g., "Summarize TechGlobal").
4. **Machine Learning Predictions:** Churn Prediction, Lead Scoring, Revenue Forecast, and Health Score generation.
5. **Next Best Action Engine:** Actionable recommendations with confidence scores and expected business impact.
6. **Executive Dashboard:** High-level metrics view showing hot leads, high-risk customers, and revenue projections.

### 4. User Flow

1. **Login:** Salesperson logs into Miracle Birds.
2. **Executive View:** Lands on the Executive Dashboard to view daily metrics and top-level AI Recommendations (Next Best Actions).
3. **Investigation:** Salesperson clicks on a high-risk customer from the dashboard.
4. **Customer 360:** Salesperson views the deep-dive Customer 360 page to read the AI Summary, view the churn probability, and analyze deal history.
5. **Action:** Salesperson asks the AI Copilot for a draft email based on the recommended Next Best Action.
6. **Resolution:** Salesperson executes the action in Frappe CRM.

### 5. Internal Architecture

Miracle Birds follows a modular monolithic approach for the MVP, which can scale into microservices:

- **Presentation Layer (Frontend):** Next.js 14, Tailwind CSS, Shadcn UI.
- **Application Layer (Backend API):** FastAPI routing, dependencies, and business logic.
- **Integration Layer:** `FrappeCRMAdapter` handling REST API communication with the Frappe CRM instance.
- **Intelligence Layer:** Abstractions to ML prediction endpoints and LLM conversational chains.

### 6. System Architecture

```
Browser (Salesperson)
  │
  ▼
Next.js 14 (Frontend UI)
  │ (REST / JSON)
  ▼
FastAPI (Backend Gateway)  ─── PostgreSQL (User Data & Cache)
  │
  ├── AI Engine (OpenAI / Gemini integration)
  ├── ML Engine (Scikit-learn / XGBoost mock implementations)
  └── CRM Integration Adapter (frappe.py)
        │
        ▼
   Frappe CRM (External System)
```

### 7. Database Schema

While the MVP relies heavily on Frappe CRM for source-of-truth data, local caching requires the following schemas (PostgreSQL):

- **User:** `id`, `email`, `hashed_password`, `tenant_id`, `role`
- **CustomerCache:** `id`, `frappe_id`, `name`, `health_score`, `churn_risk`, `last_synced_at`
- **PredictionLog:** `id`, `customer_id`, `model_type`, `prediction_value`, `confidence`, `reason`
- **AuditLog:** `id`, `user_id`, `action`, `timestamp`

### 8. API Design

- `POST /api/v1/auth/login`: Authenticate and issue JWT.
- `GET /api/v1/analytics/dashboard`: Retrieve metrics for Executive Dashboard.
- `GET /api/v1/customers`: List customers (cached from Frappe).
- `GET /api/v1/customers/{id}`: Get Customer 360 unified data.
- `POST /api/v1/copilot/chat`: Send natural language query.
- `POST /api/v1/predictions/churn`: Trigger churn calculation.
- `GET /api/v1/predictions/next-best-action/{id}`: Fetch recommended action.

### 9. Folder Structure

```
miracle-birds/
├── apps/
│   ├── frontend/             # Next.js Application
│   │   ├── src/app/(auth)    # Login pages
│   │   ├── src/app/(dashboard)# Dashboard, Customers, Copilot
│   ├── backend/              # FastAPI Application
│   │   ├── app/api/v1/       # Endpoints (customers, analytics, copilot)
│   ├── crm-integration/      # CRM Adapters
│   │   ├── app/adapters/     # frappe.py, factory.py
│   ├── ai-engine/            # LLM Orchestration
│   ├── ml-engine/            # Predictive Analytics
├── docs/                     # Documentation (PHASE_1_SDD.md)
└── infrastructure/           # Docker / K8s Deployment files
```

### 10. Development Plan

- **Day 1:** System setup, Frappe CRM API reverse-engineering, Backend schema creation.
- **Day 2:** Build FrappeCRMAdapter, establish API endpoints, and mock ML/AI responses.
- **Day 3:** Build Next.js UI (Dashboard, Customer 360, Copilot). Connect frontend to backend.
- **Day 4:** Polish UI/UX (Premium dark mode aesthetics), bug squashing, final documentation, and presentation prep.

### 11. Module Breakdown

- **Auth Module:** JWT verification, Role-based access control.
- **Dashboard Module:** Aggregates data from AI, ML, and CRM for the top-level view.
- **CRM Sync Module:** `FrappeCRMAdapter` fetches and normalizes data to the unified schema.
- **Copilot Module:** Manages chat history and forwards context to the LLM.
- **Predictive Analytics Module:** Generates health scores, lead scores, and Next Best Actions.

### 12. Team Task Allocation

- **Frontend Engineer:** Next.js scaffolding, UI implementation, Tailwind styling, React Query hooks.
- **Backend Engineer:** FastAPI endpoints, Database schema, Auth layer.
- **AI/ML Engineer:** Implementing ML mock logic, Prompt Engineering for Copilot, Explainable AI reasons.
- **Integration Engineer:** Frappe CRM API adapter, Data normalization, Webhook stubs.

### 13. Future Scope (Phase 2 & 3)

- **Phase 2 (Growth):** Real-time bidirectional syncing via Frappe Webhooks, real ML model training on historical CRM data via MLflow, Workflow Automation (email dispatching).
- **Phase 3 (Enterprise):** Voice Agent capabilities (calling customers directly), multi-tenant SaaS deployment, SOC 2 compliance features.
