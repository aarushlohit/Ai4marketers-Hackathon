# How To Run The Project

This project is a multi-service AI CRM platform. The simplest way to run it is with Docker Compose.

## Prerequisites

- Docker Desktop or Docker Engine with Compose
- Node.js 20+
- npm 10+
- Python 3.11+

## 1. Setup Environment

From the project root:

```bash
cp .env.example .env
```

For local demo mode, the default database and Redis values in `docker-compose.yml` are enough. Add real API keys or CRM credentials in `.env` only if you want live AI/CRM integrations.

## 2. Run Everything With Docker

```bash
npm install
npm run docker:up
```

This runs:

- Frontend
- Backend API
- PostgreSQL with pgvector
- Redis
- AI Engine
- ML Engine
- CRM Integration
- Security Engine
- Workflow Engine
- Agent, Memory, Knowledge, Search, Reasoning, Simulation, Executive, Customer Twin, and Observability services

## 3. Open The App

- Frontend: http://localhost:13000
- Backend API docs: http://localhost:18000/docs
- Backend health: http://localhost:18000/health

Main service ports:

| Service | URL |
| --- | --- |
| Backend API | http://localhost:18000 |
| Frontend | http://localhost:13000 |
| AI Engine | http://localhost:28001 |
| ML Engine | http://localhost:28002 |
| CRM Integration | http://localhost:28003 |
| Security Engine | http://localhost:28004 |
| Workflow Engine | http://localhost:28005 |
| Agent Service | http://localhost:28101 |
| Memory Service | http://localhost:28102 |
| Knowledge Service | http://localhost:28103 |
| Search Service | http://localhost:28104 |
| Reasoning Service | http://localhost:28105 |
| Simulation Service | http://localhost:28106 |
| Executive Service | http://localhost:28107 |
| Customer Twin Service | http://localhost:28108 |
| Observability Service | http://localhost:28109 |

## 4. Check Services

After Docker finishes starting:

```bash
python test_features.py
```

You can also check containers:

```bash
docker compose ps
docker compose logs -f backend
```

## Mock Zoho/Salesforce Connectors

The project includes a local mock CRM provider, so you can demo connector OAuth and contact fetches without real Zoho or Salesforce accounts.

Make sure `.env` keeps mock mode enabled:

```bash
CRM_MOCK_MODE=true
MOCK_CRM_PUBLIC_URL=http://localhost:28900
MOCK_CRM_INTERNAL_URL=http://mock_crm_provider:8900
```

Start the CRM integration service and mock provider:

```bash
docker compose up --build crm_integration mock_crm_provider
```

Mock provider health:

```bash
curl http://localhost:28900/health
```

Start a mock Zoho OAuth flow directly against the CRM integration service:

```bash
curl -L "http://localhost:28003/zoho/authorize?tenant_id=demo-tenant&redirect_uri=http://localhost:28003/zoho/callback"
```

Start a mock Salesforce OAuth flow:

```bash
curl -L "http://localhost:28003/salesforce/authorize?tenant_id=demo-tenant&redirect_uri=http://localhost:28003/salesforce/callback"
```

List stored mock connections:

```bash
curl "http://localhost:28003/connections?tenant_id=demo-tenant"
```

Sync a connection by replacing `<connection_id>` with the ID from the previous response:

```bash
curl -X POST "http://localhost:28003/sync/<connection_id>/start?tenant_id=demo-tenant&sync_type=full"
```

The mock Zoho connector returns contacts from `http://localhost:28900/crm/v3/Contacts`. The mock Salesforce connector returns contacts from `http://localhost:28900/services/data/v58.0/query`.

## 5. Stop Everything

```bash
npm run docker:down
```

To remove containers and volumes:

```bash
docker compose down -v
```

## Frontend Only

Use this when you only want to work on the Next.js UI:

```bash
npm install
cd apps/frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

If the backend is running through Docker, set this in the root `.env` or frontend env:

```bash
NEXT_PUBLIC_API_URL=http://localhost:18000
```

## Tests

Run the root test suite:

```bash
npm test
```

Run frontend tests directly:

```bash
cd apps/frontend
npm test
```

## Common Fixes

If Docker services are stale:

```bash
docker compose down
docker compose up --build
```

If npm dependencies are stale:

```bash
rm -rf node_modules apps/frontend/node_modules
npm install
```

If a port is already in use, stop the existing process or change the port mapping in `docker-compose.yml`.
