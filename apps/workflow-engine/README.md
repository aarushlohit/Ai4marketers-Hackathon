# ⚡ Workflow Engine — Miracle Birds

Automated workflow execution triggered by AI predictions and CRM events.

## Technology Stack

- **FastAPI** — REST API (port 8003)
- **Celery + Redis** — Async workflow execution
- **SQLAlchemy** — Workflow definitions stored in PostgreSQL

## Supported Triggers

| Trigger              | Description                                  |
| -------------------- | -------------------------------------------- |
| `churn_risk_high`    | Customer churn probability ≥ threshold       |
| `lead_score_changed` | Lead score increases/decreases significantly |
| `health_score_drop`  | Health score drops below threshold           |
| `crm_sync_completed` | After a CRM sync job finishes                |
| `scheduled`          | Cron-based time trigger                      |

## Supported Actions

| Action         | Description                       |
| -------------- | --------------------------------- |
| `send_email`   | Send templated email notification |
| `create_task`  | Create task in CRM                |
| `send_slack`   | Post message to Slack channel     |
| `call_webhook` | POST to an external webhook URL   |
| `add_tag`      | Tag customer in Miracle Birds     |

## API Endpoints

```
GET  /workflows              — List workflow definitions
POST /workflows              — Create workflow
PUT  /workflows/{id}/toggle  — Enable/disable workflow
DELETE /workflows/{id}       — Delete workflow
POST /executions/trigger     — Trigger event (from ML/Backend)
GET  /executions/{tenant_id} — List execution history
GET  /health                 — Health check
```

## Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8003
# Run Celery for async execution:
celery -A app.core.celery_app worker --loglevel=info
```
