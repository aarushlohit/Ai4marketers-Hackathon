# 📁 Miracle Birds — Project Folder Structure

```
miracle-birds/
│
├── .env.example                    # Environment variable template
├── .gitignore
├── docker-compose.yml              # Full local dev stack (13 services)
├── package.json                    # Turborepo monorepo root
├── README.md
├── FOLDER_STRUCTURE.md             # This file
│
├── .github/
│   └── workflows/
│       └── ci-cd.yaml              # GitHub Actions: test → build → deploy
│
├── apps/                           # Microservices
│   │
│   ├── frontend/                   # Next.js 14 web application (port 3000)
│   │   ├── Dockerfile
│   │   ├── Dockerfile.dev
│   │   ├── next.config.js
│   │   ├── package.json
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json
│   │   └── src/
│   │       ├── app/
│   │       │   ├── (auth)/         # Unauthenticated pages (no sidebar)
│   │       │   │   ├── login/      # Login page (RHF + Zod)
│   │       │   │   └── register/   # Registration page
│   │       │   └── (dashboard)/    # Protected pages (with sidebar)
│   │       │       ├── layout.tsx  # Sidebar + topnav shell
│   │       │       ├── overview/   # Home dashboard (KPI cards)
│   │       │       ├── customers/  # Customer list + search
│   │       │       ├── predictions/ # Churn/lead/health table
│   │       │       ├── analytics/  # Charts + time-range picker
│   │       │       ├── copilot/    # AI chat interface
│   │       │       ├── integrations/ # CRM connections panel
│   │       │       ├── workflows/  # Automation rules
│   │       │       └── settings/   # Profile, security, notifications
│   │       ├── components/
│   │       │   ├── features/
│   │       │   │   ├── analytics/  # DashboardMetrics, AnalyticsDashboard
│   │       │   │   ├── copilot/    # CopilotChat (streaming, starter prompts)
│   │       │   │   ├── customers/  # CustomerList (paginated + risk badges)
│   │       │   │   ├── integrations/ # IntegrationsPanel (OAuth + sync)
│   │       │   │   ├── predictions/ # PredictionsDashboard (risk bars)
│   │       │   │   ├── settings/   # SettingsPanel (3-tab form)
│   │       │   │   └── workflows/  # WorkflowsPanel (toggle/delete)
│   │       │   ├── layouts/        # DashboardSidebar, DashboardNav
│   │       │   └── providers.tsx   # QueryClient + ThemeProvider
│   │       ├── lib/
│   │       │   ├── api/            # client.ts (Axios + token refresh)
│   │       │   │                   # customers.ts (typed API functions)
│   │       │   ├── hooks/          # useAuth.ts
│   │       │   └── utils.ts        # cn, formatCurrency, formatPercent,
│   │       │                       # truncate, getInitials
│   │       ├── stores/             # auth.store.ts (Zustand + persist)
│   │       └── types/              # index.ts (Customer, Prediction types)
│   │
│   ├── backend/                    # FastAPI REST API (port 8000)
│   │   ├── main.py                 # FastAPI app + exception handlers
│   │   ├── requirements.txt
│   │   ├── Dockerfile / Dockerfile.dev
│   │   ├── alembic.ini             # DB migration config
│   │   ├── alembic/env.py          # Async migration environment
│   │   └── app/
│   │       ├── api/v1/
│   │       │   ├── router.py       # Aggregates all 8 routers
│   │       │   ├── dependencies.py # Auth, pagination, DB session DI
│   │       │   └── endpoints/      # auth, customers, predictions,
│   │       │                       # analytics, integrations, copilot,
│   │       │                       # users, workflows
│   │       ├── core/               # config, database (RLS), security, celery
│   │       ├── models/             # SQLAlchemy ORM: User, Customer
│   │       ├── schemas/            # Pydantic v2 schemas
│   │       ├── middleware/         # logging, rate_limit, tenant (RLS)
│   │       ├── workers/            # Celery tasks: predictions, sync
│   │       ├── exceptions/         # handlers.py (global error handling)
│   │       ├── domain/
│   │       │   ├── entities/       # CustomerEntity, UserEntity (DDD)
│   │       │   ├── value_objects/  # Email (immutable, self-validating)
│   │       │   └── events/         # CustomerCreated, CustomerChurnRiskHigh
│   │       ├── use_cases/
│   │       │   └── customer/       # GetCustomer360UseCase
│   │       ├── repositories/       # CustomerRepository, UserRepository
│   │       └── services/           # Business logic services
│   │   └── tests/
│   │       ├── conftest.py         # Fixtures: async DB, client, auth headers
│   │       ├── unit/               # Domain, security, feature engineering tests
│   │       └── integration/        # Auth + customer endpoint tests
│   │
│   ├── ai-engine/                  # LLM orchestration (port 8001)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile.dev
│   │   └── app/
│   │       ├── agents/             # crm_copilot.py (RAG + injection check)
│   │       ├── api/                # chat.py, embeddings.py
│   │       ├── chains/             # LangChain chain definitions
│   │       ├── prompts/            # Prompt templates
│   │       ├── embeddings/         # Embedding utilities
│   │       ├── memory/             # Redis conversation memory
│   │       ├── tools/              # LangChain tools (DB query, search)
│   │       └── core/               # config.py, llm.py (factory)
│   │
│   ├── ml-engine/                  # Predictive analytics (port 8002)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile.dev
│   │   ├── models/saved/           # Trained .joblib model files
│   │   └── app/
│   │       ├── api/                # predictions.py, batch.py
│   │       ├── models/             # Model class definitions
│   │       ├── features/           # feature_engineering.py (50+ features)
│   │       ├── pipelines/          # train_churn.py (XGBoost + MLflow)
│   │       ├── preprocessing/      # Data cleaning, imputation
│   │       ├── explainability/     # shap_explainer.py (TreeExplainer)
│   │       └── core/               # model_registry.py (joblib loader)
│   │
│   ├── crm-integration/            # CRM sync & OAuth (port 8003)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile.dev
│   │   └── app/
│   │       ├── adapters/           # base.py, salesforce.py, zoho.py,
│   │       │                       # hubspot.py, factory.py
│   │       ├── api/                # connections.py, sync.py, webhooks.py
│   │       ├── services/           # oauth_service.py, sync_service.py
│   │       ├── models/             # DB models for connections/jobs
│   │       ├── schemas/            # Pydantic schemas
│   │       └── core/               # config.py
│   │
│   ├── security-engine/            # AI security layer (port 8004)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile.dev
│   │   └── app/
│   │       ├── api/                # firewall.py, pii.py, audit.py
│   │       ├── core/               # firewall.py, pii_detector.py
│   │       └── governance/         # Compliance & policy enforcement
│   │
│   └── workflow-engine/            # Automation engine (port 8005)
│       ├── main.py
│       ├── requirements.txt
│       ├── Dockerfile.dev
│       └── app/
│           ├── api/                # workflows.py (CRUD), executions.py (trigger)
│           ├── core/               # config, celery
│           ├── executors/          # Action executors (email, slack, webhook)
│           └── triggers/           # Trigger evaluators (churn, score, scheduled)
│
├── infrastructure/
│   ├── database/
│   │   └── init.sql                # PostgreSQL schemas + pgvector + RLS policies
│   ├── kubernetes/
│   │   ├── base/                   # All service deployments (HPA, Services)
│   │   │                           # backend, frontend, ai-engine, ml-engine,
│   │   │                           # crm-integration, security-engine, ingress
│   │   └── overlays/
│   │       ├── production/
│   │       └── staging/
│   ├── terraform/
│   │   ├── main.tf                 # VPC, EKS, RDS, ElastiCache, S3
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/
│       ├── prometheus/             # prometheus.yml, alerts.yml
│       └── grafana/                # dashboards.json
│
├── docs/
│   ├── TECHNICAL_BLUEPRINT.md      # Master project index
│   ├── SRS.md                      # Software Requirements Specification
│   ├── SDD.md                      # Software Design Document
│   ├── architecture/
│   │   ├── SYSTEM_ARCHITECTURE.md
│   │   └── CRM_INTEGRATION_ARCHITECTURE.md
│   ├── api/
│   │   ├── openapi.yaml            # OpenAPI 3.0 specification
│   │   └── API_DOCUMENTATION.md    # Developer-facing API guide
│   ├── database/
│   │   └── DATABASE_SCHEMA.md
│   ├── security/
│   │   └── SECURITY_ARCHITECTURE.md
│   └── deployment/
│       └── DEPLOYMENT_GUIDE.md
│
└── scripts/
    ├── setup_engines.ps1           # Create engine directory structure
    ├── setup_crm.ps1               # Create CRM integration dirs
    └── verify.ps1                  # Verify all Dockerfiles + file counts
```

## Service Port Map

| Service         | Host Port | Container Port | Technology               |
| --------------- | --------- | -------------- | ------------------------ |
| Frontend        | 3000      | 3000           | Next.js 14               |
| Backend API     | 8000      | 8000           | FastAPI                  |
| AI Engine       | 8001      | 8001           | LangChain + FastAPI      |
| ML Engine       | 8002      | 8002           | XGBoost + FastAPI        |
| CRM Integration | 8003      | 8003           | FastAPI + Celery         |
| Security Engine | 8004      | 8004           | FastAPI + spaCy          |
| Workflow Engine | 8005      | 8003           | FastAPI + Celery         |
| PostgreSQL      | 5432      | 5432           | PostgreSQL 16 + pgvector |
| Redis           | 6379      | 6379           | Redis 7                  |
| MLflow          | 5000      | 5000           | MLflow                   |
| Grafana         | 3001      | 3000           | Grafana                  |
| Prometheus      | 9090      | 9090           | Prometheus               |

## Test Coverage

| Service   | Unit Tests                                                            | Integration Tests             |
| --------- | --------------------------------------------------------------------- | ----------------------------- |
| Backend   | CustomerEntity, UserEntity, Email VO, JWT/bcrypt, Feature Engineering | Auth endpoints, Customer CRUD |
| Frontend  | utils (cn, formatCurrency, formatPercent, truncate, getInitials)      | —                             |
| ML Engine | Feature engineering (13 tests)                                        | —                             |
