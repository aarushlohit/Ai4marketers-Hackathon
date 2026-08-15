# 🐦 Miracle Birds

Miracle Birds is a production-oriented AI intelligence layer for CRM teams. It connects customer data, predictions, workflows, and conversational analysis in one workspace so revenue teams can decide what to do next.

## Product

- Customer 360 with health, deal, and activity context
- AI Copilot for customer and pipeline questions
- Churn prediction, lead scoring, and revenue forecasting
- Next-best-action recommendations and workflow automation
- OAuth integrations for Salesforce, Zoho, HubSpot, Microsoft Dynamics 365, and Pipedrive
- Tenant isolation, JWT authentication, MFA support, audit logging, rate limiting, and security headers

## Production URLs

| Service | URL |
| --- | --- |
| Web application | https://miracle-birds-crm-frontend.vercel.app |
| Backend API | https://mb-backend-rnhn.onrender.com |
| Backend health | https://mb-backend-rnhn.onrender.com/health |
| CRM integration health | https://mb-crm-integration.onrender.com/health |

The production frontend is deployed on Vercel. Backend services and managed data services are deployed in Render. The Render service definitions are in `render.yaml`.

## Demo access

The shared demo account is for demonstrations only and must never be used for customer data or production administration.

| Field | Value |
| --- | --- |
| Username | `demo@miraclebirds.ai` |
| Password | `Demo@123456` |

Rotate or disable this account before any public launch. Do not reuse this password for another environment. Demo data is non-production sample data.

## How to use the application

1. Open the web application URL.
2. Choose **Sign in** and enter the demo credentials, or choose **Create account**.
3. Open **Overview** to review pipeline and customer health signals.
4. Use **Customers** to inspect customer profiles, scores, and activity.
5. Use **Copilot** to ask questions about the connected CRM workspace.
6. Use **Predictions** to review churn, lead, and revenue signals.
7. Use **Workflows** to configure actions triggered by CRM or AI events.
8. Use **Integrations** to connect a CRM through its OAuth provider.
9. Use **Settings** and **Security Center** to configure account security, MFA, and audit visibility.

## Architecture

```text
Browser
  |
  v
Next.js frontend on Vercel
  |
  v
FastAPI backend on Render
  |-------- PostgreSQL and Redis on Render
  |-------- AI engine
  |-------- CRM integration service
  |-------- Security engine
  |-------- Workflow engine
```

The backend is the authorization boundary. Client-side state is not trusted for tenant, role, customer, or workflow access. Service-to-service calls use `X-Internal-API-Key` and require a configured secret in production.

## Security model

- Passwords are hashed with bcrypt.
- Access and refresh JWTs are signed with environment-provided secrets.
- Refresh tokens rotate and are revocable server-side.
- Login failures are protected by brute-force controls.
- API requests use exact configured CORS origins.
- Internal endpoints reject missing or invalid service credentials.
- Security headers include CSP, HSTS in production, X-Frame-Options, nosniff, Referrer-Policy, Permissions-Policy, COOP, and CORP.
- Rate limiting is enforced through Redis-backed middleware.
- OAuth state values are generated cryptographically and validated during callbacks.
- Secrets belong in Render or Vercel environment variables, never in source control.
- Do not claim SOC 2, HIPAA, GDPR, or other certification without an independently verified compliance program.

## Required production configuration

Set these values in the deployment provider's secret manager before enabling production traffic:

| Variable | Purpose |
| --- | --- |
| `ENVIRONMENT=production` | Enables production safeguards |
| `JWT_SECRET` | At least 32 random characters |
| `SECRET_KEY` | At least 32 random characters |
| `INTERNAL_API_KEY` | Service-to-service authentication |
| `ALLOWED_ORIGINS` | Comma-separated exact frontend origins |
| `TRUSTED_HOSTS` | Comma-separated approved hostnames |
| `DATABASE_URL` | Managed PostgreSQL connection |
| `REDIS_URL` | Managed Redis connection |
| `OPENCODE_API_KEY` | OpenCode Zen API credential for Executive AI and CRM Copilot |
| `OPENCODE_MODEL` | OpenCode model ID; defaults to `deepseek-v4-flash-free` |
| `OPENCODE_API_URL` | OpenAI-compatible endpoint; defaults to `https://opencode.ai/zen/v1/chat/completions` |
| CRM OAuth variables | Provider-specific client IDs, secrets, and redirect settings |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Optional knowledge graph connection |

Production startup rejects insecure JWT and application secrets. Missing internal credentials cause protected service calls to fail closed.

## Deployment operations

### Vercel

From `apps/frontend`:

```bash
vercel link --yes --project miracle-birds-crm-frontend --scope ashlinmirshas-projects
vercel deploy --prod --yes --scope ashlinmirshas-projects
```

Verify the deployment:

```bash
curl -fsS https://miracle-birds-crm-frontend.vercel.app/
curl -fsS https://miracle-birds-crm-frontend.vercel.app/login
curl -fsS https://miracle-birds-crm-frontend.vercel.app/register
```

### Render

Authenticate and inspect the active workspace:

```bash
render login
render whoami
render services --output json
```

Inspect or trigger a service deployment using its Render service ID:

```bash
render deploys list SERVICE_ID --output json
render deploys create SERVICE_ID
render logs --resources SERVICE_ID --limit 100 --output json
```

Verify health endpoints after deployment:

```bash
curl -fsS https://mb-backend-rnhn.onrender.com/health
curl -fsS https://mb-crm-integration.onrender.com/health
curl -fsS https://mb-ai-engine.onrender.com/health
curl -fsS https://mb-security-engine.onrender.com/health
```

Do not treat a Render deployment marked `succeeded` as proof that an AI provider, CRM OAuth flow, database migration, or downstream service is working. Verify the HTTP response and relevant application logs.

## Verification commands

Frontend checks:

```bash
cd apps/frontend
npm ci
npm run type-check
npm test -- --runInBand
npm run build
```

Backend checks:

```bash
python3 -m pip install -r apps/backend/requirements.txt
python3 -m pytest apps/backend/tests -q
python3 -m pytest apps/crm-integration/tests apps/mock-crm-provider/tests -q
```

Dependency checks:

```bash
npm audit --omit=dev
python3 -m pip check
```

Security review before release:

1. Confirm production secrets are set in Render and Vercel.
2. Confirm no `.env` file, token, password, or private key is tracked by Git.
3. Confirm CORS contains only approved production origins.
4. Confirm invalid internal API keys return `401`.
5. Confirm login, refresh, logout, MFA, and rate-limit behavior.
6. Confirm every service health endpoint and one authenticated AI request.
7. Review Render logs for failed deploys, authentication failures, and downstream errors.
8. Run a dependency audit and resolve high or critical findings before release.

## Repository map

| Path | Responsibility |
| --- | --- |
| `apps/frontend` | Next.js application |
| `apps/backend` | Primary FastAPI API and authentication boundary |
| `apps/crm-integration` | CRM OAuth, sync, and webhook service |
| `apps/security-engine` | Prompt and PII security service |
| `apps/ai-engine` | AI provider orchestration |
| `apps/workflow-engine` | Workflow execution and rollback |
| `docs/api` | API reference and OpenAPI specification |
| `docs/security` | Security architecture and controls |
| `render.yaml` | Render service definitions |

## Support and incident response

For a production incident, preserve the Render deployment ID, request ID, UTC timestamp, affected account or tenant ID, endpoint, and sanitized error response. Never attach passwords, access tokens, refresh tokens, OAuth client secrets, or full request bodies to an issue.

## License

Proprietary. Copyright 2026 Miracle Birds. All rights reserved.
