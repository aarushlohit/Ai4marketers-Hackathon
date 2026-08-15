# Software Requirements Specification (SRS)

## Miracle Birds — AI Intelligence Layer for CRM

**Document ID:** MB-SRS-001  
**Version:** 1.0  
**Date:** July 13, 2026  
**Status:** Approved  
**Classification:** Confidential

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [System Constraints](#5-system-constraints)
6. [External Interface Requirements](#6-external-interface-requirements)
7. [AI Module Requirements](#7-ai-module-requirements)
8. [Security Requirements](#8-security-requirements)
9. [Compliance Requirements](#9-compliance-requirements)
10. [Acceptance Criteria](#10-acceptance-criteria)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification describes the functional and non-functional requirements for **Miracle Birds**, an enterprise AI Intelligence Layer that enhances existing Customer Relationship Management (CRM) platforms with AI-powered insights, predictive analytics, and workflow automation.

### 1.2 Scope

Miracle Birds is NOT a CRM system. It is an AI Intelligence Layer that:

- Connects to existing CRM platforms via secure OAuth APIs
- Transforms raw customer data into intelligent business decisions
- Provides real-time AI predictions and recommendations
- Automates workflows based on AI-driven triggers
- Delivers enterprise-grade security and compliance

**In Scope:**

- AI CRM Copilot
- Customer 360 Intelligence
- Predictive Analytics (churn, lead scoring, revenue, health score)
- Next Best Action Engine
- Meeting Intelligence
- Executive AI Copilot
- Workflow Automation
- CRM Integration Layer (Salesforce, Zoho, HubSpot, Dynamics, Pipedrive)
- Security & Compliance (GDPR, SOC 2, HIPAA)
- Multi-tenant SaaS Architecture

**Out of Scope (Future):**

- Customer Digital Twin
- Reinforcement Learning Optimization
- Autonomous Workflow Execution
- Voice AI Assistant

### 1.3 Definitions

| Term                  | Definition                                                                    |
| --------------------- | ----------------------------------------------------------------------------- |
| AI Intelligence Layer | Software that adds AI capabilities to existing systems without replacing them |
| Tenant                | An enterprise customer subscribing to Miracle Birds SaaS                      |
| CRM                   | Customer Relationship Management system (Salesforce, Zoho, etc.)              |
| Churn                 | Customer cancellation or disengagement                                        |
| Lead Score            | Numerical rating of a prospect's likelihood to become a customer              |
| Health Score          | Composite score representing customer relationship quality                    |
| RBAC                  | Role-Based Access Control                                                     |
| PII                   | Personally Identifiable Information                                           |
| LLM                   | Large Language Model (e.g., GPT-4, Gemini)                                    |

### 1.4 References

- System Architecture Document (docs/architecture/SYSTEM_ARCHITECTURE.md)
- Database Schema (docs/database/DATABASE_SCHEMA.md)
- API Documentation (docs/api/API_DOCUMENTATION.md)
- Security Architecture (docs/security/SECURITY_ARCHITECTURE.md)
- Deployment Guide (docs/deployment/DEPLOYMENT_GUIDE.md)

---

## 2. Overall Description

### 2.1 Product Perspective

Miracle Birds operates as a middleware intelligence layer between enterprise users and their existing CRM systems.

```
┌──────────────┐     ┌─────────────────────────┐     ┌─────────────┐
│  Enterprise  │────▶│     Miracle Birds        │────▶│    CRM      │
│    Users     │◀────│  AI Intelligence Layer  │◀────│  Platforms  │
└──────────────┘     └─────────────────────────┘     └─────────────┘
                              │
                     ┌────────┴────────┐
                     │   AI/ML Engine  │
                     │  (OpenAI/XGBoost│
                     │  /LangChain)    │
                     └─────────────────┘
```

### 2.2 User Classes

| User Class   | Description                                          | Priority |
| ------------ | ---------------------------------------------------- | -------- |
| Super Admin  | Platform administrator with full system access       | Critical |
| Tenant Admin | Organization administrator managing their instance   | Critical |
| Manager      | Team manager with reporting and configuration access | High     |
| Sales User   | Standard user accessing customers and predictions    | High     |
| Viewer       | Read-only access for stakeholders                    | Medium   |
| API Consumer | External systems integrating via API                 | High     |

### 2.3 Operating Environment

- **Cloud:** AWS (us-east-1 primary, multi-region optional)
- **Container Orchestration:** Kubernetes (EKS)
- **Database:** PostgreSQL 16 with pgvector extension
- **Cache:** Redis 7 (ElastiCache)
- **AI Models:** OpenAI GPT-4, Google Gemini Pro
- **Browser Support:** Chrome 120+, Firefox 120+, Edge 120+, Safari 17+

---

## 3. Functional Requirements

### 3.1 Authentication & Authorization

| ID          | Requirement                                                               | Priority    |
| ----------- | ------------------------------------------------------------------------- | ----------- |
| FR-AUTH-001 | Users shall be able to register with email and password                   | Must Have   |
| FR-AUTH-002 | Users shall be able to login with email/password returning JWT tokens     | Must Have   |
| FR-AUTH-003 | Access tokens shall expire after 30 minutes                               | Must Have   |
| FR-AUTH-004 | Refresh tokens shall expire after 7 days                                  | Must Have   |
| FR-AUTH-005 | System shall support Multi-Factor Authentication (TOTP)                   | Must Have   |
| FR-AUTH-006 | System shall implement RBAC with 5 role levels                            | Must Have   |
| FR-AUTH-007 | System shall support OAuth 2.0 SSO for enterprise (SAML optional)         | Should Have |
| FR-AUTH-008 | Failed login attempts shall be rate-limited (5 attempts → 15 min lockout) | Must Have   |

### 3.2 Customer Management

| ID          | Requirement                                                               | Priority    |
| ----------- | ------------------------------------------------------------------------- | ----------- |
| FR-CUST-001 | System shall display paginated customer list with search and filters      | Must Have   |
| FR-CUST-002 | System shall provide Customer 360 view with all intelligence aggregated   | Must Have   |
| FR-CUST-003 | Users shall be able to create, read, update, and delete customer records  | Must Have   |
| FR-CUST-004 | System shall track customer interaction history (calls, emails, meetings) | Must Have   |
| FR-CUST-005 | System shall display customer timeline of all events                      | Should Have |
| FR-CUST-006 | System shall support bulk operations on customer records                  | Should Have |
| FR-CUST-007 | System shall maintain complete audit trail of all changes                 | Must Have   |

### 3.3 AI Predictions

| ID          | Requirement                                                                   | Priority    |
| ----------- | ----------------------------------------------------------------------------- | ----------- |
| FR-PRED-001 | System shall predict customer churn probability (0–1 score)                   | Must Have   |
| FR-PRED-002 | Churn prediction shall include top contributing factors with SHAP explanation | Must Have   |
| FR-PRED-003 | System shall calculate lead scores (0–100) with letter grade                  | Must Have   |
| FR-PRED-004 | System shall forecast customer revenue for configurable time horizons         | Must Have   |
| FR-PRED-005 | System shall compute Customer Health Score from multiple dimensions           | Must Have   |
| FR-PRED-006 | System shall calculate Customer Lifetime Value (CLV)                          | Should Have |
| FR-PRED-007 | All predictions shall include confidence scores                               | Must Have   |
| FR-PRED-008 | Predictions shall be refreshed on a configurable schedule                     | Must Have   |
| FR-PRED-009 | System shall support explainable AI (XAI) output for all predictions          | Must Have   |

### 3.4 AI Copilot

| ID         | Requirement                                                               | Priority    |
| ---------- | ------------------------------------------------------------------------- | ----------- |
| FR-COP-001 | Users shall be able to converse with an AI assistant about their CRM data | Must Have   |
| FR-COP-002 | Copilot shall have context of current user's customer data                | Must Have   |
| FR-COP-003 | Copilot shall remember conversation history within a session              | Must Have   |
| FR-COP-004 | Copilot shall suggest follow-up actions                                   | Should Have |
| FR-COP-005 | Copilot shall support natural language queries about analytics            | Must Have   |
| FR-COP-006 | Executive Copilot shall generate weekly/monthly business summaries        | Should Have |
| FR-COP-007 | Meeting Intelligence shall transcribe and summarize meeting recordings    | Should Have |

### 3.5 Next Best Action Engine

| ID         | Requirement                                                            | Priority    |
| ---------- | ---------------------------------------------------------------------- | ----------- |
| FR-NBA-001 | System shall recommend the next best action for each customer          | Must Have   |
| FR-NBA-002 | Actions shall be ranked by expected revenue impact                     | Must Have   |
| FR-NBA-003 | Actions shall include: follow-up, upsell, retention, referral, support | Must Have   |
| FR-NBA-004 | Users shall be able to accept, dismiss, or defer recommended actions   | Must Have   |
| FR-NBA-005 | System shall learn from accepted/rejected actions over time            | Should Have |

### 3.6 Workflow Automation

| ID        | Requirement                                                                        | Priority  |
| --------- | ---------------------------------------------------------------------------------- | --------- |
| FR-WF-001 | Users shall be able to define automated workflows with trigger conditions          | Must Have |
| FR-WF-002 | Triggers shall include: churn risk threshold, lead score change, health score drop | Must Have |
| FR-WF-003 | Actions shall include: send email, create task, send Slack message, webhook        | Must Have |
| FR-WF-004 | Workflows shall execute asynchronously (not blocking user actions)                 | Must Have |
| FR-WF-005 | System shall log all workflow executions with status and output                    | Must Have |
| FR-WF-006 | Users shall be able to enable, disable, and delete workflows                       | Must Have |

### 3.7 CRM Integration

| ID         | Requirement                                                      | Priority    |
| ---------- | ---------------------------------------------------------------- | ----------- |
| FR-INT-001 | System shall connect to Salesforce via OAuth 2.0                 | Must Have   |
| FR-INT-002 | System shall connect to Zoho CRM via OAuth 2.0                   | Must Have   |
| FR-INT-003 | System shall connect to HubSpot via OAuth 2.0                    | Must Have   |
| FR-INT-004 | System shall connect to Microsoft Dynamics 365 via OAuth 2.0     | Must Have   |
| FR-INT-005 | System shall connect to Pipedrive via OAuth 2.0                  | Should Have |
| FR-INT-006 | System shall perform bi-directional data synchronization         | Must Have   |
| FR-INT-007 | System shall support real-time sync via webhooks                 | Must Have   |
| FR-INT-008 | System shall support scheduled incremental sync (hourly default) | Must Have   |
| FR-INT-009 | System shall perform full initial sync on first connection       | Must Have   |
| FR-INT-010 | Sync conflicts shall default to CRM as source of truth           | Must Have   |

### 3.8 Analytics & Reporting

| ID         | Requirement                                                                           | Priority    |
| ---------- | ------------------------------------------------------------------------------------- | ----------- |
| FR-ANA-001 | System shall provide a real-time analytics dashboard                                  | Must Have   |
| FR-ANA-002 | Dashboard shall show: total customers, churn rate, health score avg, revenue forecast | Must Have   |
| FR-ANA-003 | System shall support time range filtering (7d, 30d, 90d, 1y)                          | Must Have   |
| FR-ANA-004 | System shall allow report generation and export (CSV, PDF)                            | Should Have |
| FR-ANA-005 | System shall show customer cohort analysis                                            | Should Have |

### 3.9 Multi-Tenant Management

| ID        | Requirement                                          | Priority    |
| --------- | ---------------------------------------------------- | ----------- |
| FR-MT-001 | System shall completely isolate data between tenants | Must Have   |
| FR-MT-002 | Each tenant shall have configurable feature flags    | Must Have   |
| FR-MT-003 | Super admins shall be able to manage all tenants     | Must Have   |
| FR-MT-004 | Tenants shall be billable independently              | Should Have |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID           | Requirement                 | Target        |
| ------------ | --------------------------- | ------------- |
| NFR-PERF-001 | API response time (P95)     | < 200ms       |
| NFR-PERF-002 | AI prediction latency (P95) | < 2 seconds   |
| NFR-PERF-003 | Dashboard load time         | < 3 seconds   |
| NFR-PERF-004 | CRM webhook processing      | < 1 second    |
| NFR-PERF-005 | Full CRM sync (10K records) | < 30 minutes  |
| NFR-PERF-006 | Concurrent users supported  | 10,000+       |
| NFR-PERF-007 | API throughput              | 1,000 req/sec |

### 4.2 Availability & Reliability

| ID            | Requirement                    | Target                          |
| ------------- | ------------------------------ | ------------------------------- |
| NFR-AVAIL-001 | System uptime (SLA)            | 99.9% (< 8.7 hrs downtime/year) |
| NFR-AVAIL-002 | Recovery Time Objective (RTO)  | < 1 hour                        |
| NFR-AVAIL-003 | Recovery Point Objective (RPO) | < 15 minutes                    |
| NFR-AVAIL-004 | Database failover time         | < 60 seconds (Multi-AZ)         |
| NFR-AVAIL-005 | Zero-downtime deployments      | Required                        |

### 4.3 Scalability

| ID            | Requirement                 | Target                       |
| ------------- | --------------------------- | ---------------------------- |
| NFR-SCALE-001 | Customer records per tenant | 1,000,000+                   |
| NFR-SCALE-002 | Total tenants supported     | 10,000+                      |
| NFR-SCALE-003 | API pod auto-scaling        | 3–10 pods (CPU/memory-based) |
| NFR-SCALE-004 | Database horizontal scaling | Read replicas supported      |
| NFR-SCALE-005 | Storage auto-scaling        | 100 GB → 1 TB automatic      |

### 4.4 Security

| ID          | Requirement                | Standard                        |
| ----------- | -------------------------- | ------------------------------- |
| NFR-SEC-001 | Encryption at rest         | AES-256                         |
| NFR-SEC-002 | Encryption in transit      | TLS 1.3 minimum                 |
| NFR-SEC-003 | JWT token expiry           | Access: 30 min, Refresh: 7 days |
| NFR-SEC-004 | Password hashing           | bcrypt with cost factor ≥ 12    |
| NFR-SEC-005 | PII detection and masking  | Regex + NER model               |
| NFR-SEC-006 | Prompt injection detection | Pattern + ML (< 100ms)          |
| NFR-SEC-007 | Audit log retention        | 90 days minimum                 |
| NFR-SEC-008 | Vulnerability scanning     | Weekly automated scans          |

### 4.5 Maintainability

- **Code Coverage:** ≥ 80% for all services
- **Linting:** Enforced via CI (flake8, ESLint)
- **Type Safety:** Python type hints + TypeScript strict mode
- **Documentation:** All public APIs documented in OpenAPI 3.0
- **Dependency Updates:** Automated via Dependabot

---

## 5. System Constraints

### 5.1 Technology Constraints

- Backend must use **Python 3.11+** with **FastAPI**
- Frontend must use **Next.js 14** with **TypeScript**
- Database must be **PostgreSQL 16** with **pgvector** extension
- AI orchestration must use **LangChain / LangGraph**
- Container runtime must be **Docker** with **Kubernetes** orchestration
- Cloud provider must be **AWS**

### 5.2 Business Constraints

- Must be deployable as a multi-tenant SaaS product
- Must support enterprise SSO (OAuth 2.0 minimum, SAML optional)
- Must be compliant with GDPR and SOC 2 Type II from day one
- API must be versioned for backward compatibility

---

## 6. External Interface Requirements

### 6.1 User Interfaces

- Web application accessible at `https://miraclebirds.ai`
- Responsive design supporting desktop (1280px+) and tablet (768px+)
- Accessibility: WCAG 2.1 AA compliance
- Color scheme: professional enterprise theme (Shadcn UI)

### 6.2 External API Interfaces

| System                 | Protocol | Authentication       | Version     |
| ---------------------- | -------- | -------------------- | ----------- |
| Salesforce             | REST     | OAuth 2.0            | v58.0       |
| Zoho CRM               | REST     | OAuth 2.0            | v3          |
| HubSpot                | REST     | OAuth 2.0            | v3          |
| Microsoft Dynamics 365 | OData    | OAuth 2.0 (Azure AD) | v9.2        |
| Pipedrive              | REST     | OAuth 2.0            | v1          |
| OpenAI                 | REST     | API Key              | gpt-4-turbo |
| Google Gemini          | REST     | API Key              | gemini-pro  |

### 6.3 Communication Interfaces

- HTTPS for all external communication (TLS 1.3)
- WebSocket for real-time dashboard updates
- Webhooks for event-driven CRM sync
- Redis Pub/Sub for internal service communication

---

## 7. AI Module Requirements

### 7.1 Customer Intelligence Engine

**Purpose:** Provide 360-degree customer intelligence by aggregating, analyzing, and interpreting all customer data.

| ID         | Requirement                                                     |
| ---------- | --------------------------------------------------------------- |
| AI-CIE-001 | Aggregate customer data from CRM, interactions, and predictions |
| AI-CIE-002 | Generate natural language customer summaries using LLM          |
| AI-CIE-003 | Calculate composite health score from 5+ dimensions             |
| AI-CIE-004 | Identify customer segments automatically (K-Means clustering)   |
| AI-CIE-005 | Surface anomalies and unusual patterns in customer behavior     |

### 7.2 Predictive Analytics Engine

**Churn Prediction Model:**

- Algorithm: XGBoost with 50+ features
- Target metric: AUC-ROC > 0.85
- Retraining: Weekly or on significant data drift
- Explainability: SHAP values for top 5 factors

**Lead Scoring Model:**

- Algorithm: Random Forest with 40+ features
- Output: 0–100 score with A–F grade
- Update frequency: Daily

**Revenue Forecasting Model:**

- Algorithm: Gradient Boosted Trees + ARIMA for time series
- Horizons: 30, 60, 90 days
- Accuracy target: MAPE < 15%

### 7.3 Security Intelligence Engine

| ID         | Requirement                                              |
| ---------- | -------------------------------------------------------- |
| AI-SEC-001 | Prompt injection detection with < 5% false positive rate |
| AI-SEC-002 | PII detection accuracy > 95% for all supported PII types |
| AI-SEC-003 | Secret scanning with < 100ms latency                     |
| AI-SEC-004 | Anomalous access pattern detection within 15 minutes     |

---

## 8. Security Requirements

| ID     | Requirement                                                       | Standard    |
| ------ | ----------------------------------------------------------------- | ----------- |
| SR-001 | All data in transit encrypted with TLS 1.3                        | OWASP A02   |
| SR-002 | All data at rest encrypted with AES-256                           | OWASP A02   |
| SR-003 | All API endpoints require authentication except /health and /auth | OWASP A01   |
| SR-004 | SQL injection prevention via parameterized queries (ORM)          | OWASP A03   |
| SR-005 | XSS prevention via output encoding and CSP headers                | OWASP A03   |
| SR-006 | CSRF protection on all state-changing endpoints                   | OWASP A01   |
| SR-007 | Rate limiting on authentication endpoints (5 req/min)             | OWASP A04   |
| SR-008 | All AI prompts pass through injection firewall before LLM         | AI-specific |
| SR-009 | All AI responses scanned for PII before delivery                  | AI-specific |
| SR-010 | Complete audit log of all user actions retained 90 days           | Compliance  |

---

## 9. Compliance Requirements

| Standard       | Requirement                            | Implementation         |
| -------------- | -------------------------------------- | ---------------------- |
| GDPR Art. 17   | Right to erasure within 30 days        | Anonymization API      |
| GDPR Art. 15   | Right to access — export all data      | Data export API        |
| GDPR Art. 20   | Right to portability — JSON/CSV export | Export endpoints       |
| GDPR Art. 33   | Breach notification within 72 hours    | Incident response plan |
| SOC 2 CC6      | Logical access controls                | RBAC + MFA             |
| SOC 2 CC7      | System monitoring                      | Prometheus + Grafana   |
| HIPAA §164.312 | Access controls and audit trails       | RBAC + audit log       |
| CCPA §1798.105 | Right to delete                        | Same as GDPR erasure   |

---

## 10. Acceptance Criteria

### 10.1 Functional Acceptance

- [ ] All FR-AUTH requirements pass integration tests
- [ ] Churn prediction achieves AUC-ROC > 0.85 on test dataset
- [ ] Lead scoring returns results in < 2 seconds (P95)
- [ ] CRM sync completes initial import of 10K records in < 30 minutes
- [ ] AI Copilot responds in < 5 seconds for standard queries
- [ ] Workflow automation triggers fire within 60 seconds of condition met

### 10.2 Performance Acceptance

- [ ] API P95 latency < 200ms under 1,000 concurrent users
- [ ] System sustains 99.9% uptime over 30-day observation period
- [ ] Database failover completes in < 60 seconds (Multi-AZ test)

### 10.3 Security Acceptance

- [ ] Penetration test passes with no critical/high findings
- [ ] OWASP Top 10 scan passes all checks
- [ ] Trivy container scan shows 0 critical vulnerabilities
- [ ] GDPR data export and erasure APIs function correctly

---

**Document Version:** 1.0  
**Approved By:** Engineering Lead  
**Date:** July 13, 2026  
**Next Review:** January 13, 2027
