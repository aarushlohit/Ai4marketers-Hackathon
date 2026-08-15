"""Observability Service — entry point for Prometheus metrics, centralized logs and tracing."""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app, Counter, Histogram
import time
import structlog

logger = structlog.get_logger()

app = FastAPI(
    title="Miracle Birds Observability Service",
    description="Observability and diagnostics metrics aggregator",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics setup
REQUEST_COUNT = Counter("observability_requests_total", "Total requests received", ["method", "endpoint", "status"])
LATENCY_HIST = Histogram("observability_request_latency_seconds", "Request execution latency")

# Expose Prometheus ASGI metrics app under /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def record_metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    latency = time.time() - start_time
    
    LATENCY_HIST.observe(latency)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "observability-service"}

@app.get("/api/v3/observability/logs")
async def search_logs(query: str = "", level: str = "INFO", limit: int = 50):
    """Retrieve simulated centralized log output."""
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    logs = [
        {"timestamp": now_str, "level": "INFO", "service": "backend", "message": "User login success for tenant 00000000-0000-0000-0000-000000000001"},
        {"timestamp": now_str, "level": "INFO", "service": "agent_service", "message": "Executive agent delegated task query to Sales Agent"},
        {"timestamp": now_str, "level": "INFO", "service": "workflow_engine", "message": "Workflow 'Risk Escalation' completed successfully in 420ms"},
        {"timestamp": now_str, "level": "WARNING", "service": "security_engine", "message": "PII detector masked outbound email address field in customer twin response"}
    ]
    if query:
        logs = [log for log in logs if query.lower() in log["message"].lower() or query.lower() in log["service"].lower()]
    return {"logs": logs[:limit], "total": len(logs)}

@app.get("/api/v3/observability/traces")
async def get_distributed_traces(limit: int = 10):
    """Retrieve simulated open telemetry distributed call graphs."""
    return {
        "traces": [
            {
                "trace_id": "tr_8f9c2d7e0a1b",
                "name": "API Request: /briefing",
                "latency_ms": 1240,
                "spans": [
                    {"span_id": "sp_1", "name": "backend:get_executive_briefing", "latency_ms": 1240},
                    {"span_id": "sp_2", "parent_id": "sp_1", "name": "ai_engine:executive/briefing", "latency_ms": 1180},
                    {"span_id": "sp_3", "parent_id": "sp_2", "name": "security_engine:firewall/scan", "latency_ms": 80}
                ]
            },
            {
                "trace_id": "tr_1a2b3c4d5e6f",
                "name": "Workflow Execution: Trigger",
                "latency_ms": 480,
                "spans": [
                    {"span_id": "sp_10", "name": "workflow_engine:trigger_event", "latency_ms": 480},
                    {"span_id": "sp_11", "parent_id": "sp_10", "name": "celery:run_workflow_execution", "latency_ms": 420}
                ]
            }
        ]
    }

@app.get("/api/v3/observability/costs")
async def get_llm_cost_summary():
    """Retrieve a breakdown of aggregated LLM token expenditures."""
    return {
        "total_cost_usd": 124.52,
        "period": "current_month",
        "service_distribution": {
            "ai_engine": 84.12,
            "agent_service": 32.40,
            "copilot": 8.00
        },
        "model_distribution": {
            "gpt-4": 112.52,
            "gpt-3.5-turbo": 12.00
        }
    }
