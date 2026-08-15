# 🔗 CRM Integration Service - Miracle Birds

## Unified CRM Integration Layer

### Purpose

Connect Miracle Birds AI Intelligence Platform with external CRM systems (Salesforce, Zoho CRM, HubSpot, Microsoft Dynamics 365, Pipedrive) through secure OAuth authentication and bi-directional data synchronization.

---

## Technology Stack

- **FastAPI** - REST API framework
- **Python 3.11+** - Programming language
- **SQLAlchemy** - ORM for database operations
- **Celery** - Async task processing for sync jobs
- **Redis** - Task queue and rate limiting
- **PostgreSQL** - Connection and sync metadata storage

---

## Folder Structure

```
apps/crm-integration/
├── app/
│   ├── adapters/              # CRM-specific adapters
│   │   ├── __init__.py
│   │   ├── base.py           # Base adapter interface
│   │   ├── salesforce.py     # Salesforce adapter
│   │   ├── zoho.py           # Zoho CRM adapter
│   │   ├── hubspot.py        # HubSpot adapter
│   │   ├── dynamics.py       # Microsoft Dynamics adapter
│   │   └── pipedrive.py      # Pipedrive adapter
│   ├── services/             # Business logic
│   │   ├── oauth_service.py  # OAuth flow management
│   │   ├── sync_service.py   # Data synchronization
│   │   ├── webhook_service.py # Webhook processing
│   │   ├── token_manager.py  # Token refresh logic
│   │   └── conflict_resolver.py # Conflict resolution
│   ├── api/                  # REST endpoints
│   │   ├── connections.py    # CRM connection endpoints
│   │   ├── sync.py           # Sync management endpoints
│   │   └── webhooks.py       # Webhook handlers
│   ├── models/               # Database models
│   │   ├── connection.py     # CRM connection model
│   │   └── sync_job.py       # Sync job model
│   ├── schemas/              # Pydantic schemas
│   │   ├── connection.py
│   │   └── sync.py
│   └── core/                 # Core utilities
│       ├── config.py         # Configuration
│       ├── rate_limiter.py   # Rate limit management
│       └── mapper.py         # Data mapping utilities
├── requirements.txt
├── Dockerfile
└── main.py
```

---

## Core Components

### 1. CRM Adapters

**Purpose**: Provide unified interface for different CRM platforms

**Supported CRMs**:

- ✅ Salesforce (REST API v58.0)
- ✅ Zoho CRM (v3)
- ✅ HubSpot (v3)
- ✅ Microsoft Dynamics 365 (Web API v9.2)
- ✅ Pipedrive (v1)

**Adapter Interface**:

```python
class CRMAdapter(ABC):
    @abstractmethod
    async def authenticate(self) -> bool

    @abstractmethod
    async def get_contacts(self, filters, limit) -> List[Dict]

    @abstractmethod
    async def create_contact(self, data) -> Dict

    @abstractmethod
    async def update_contact(self, id, data) -> Dict

    @abstractmethod
    def map_to_unified(self, crm_data) -> Dict

    @abstractmethod
    def map_from_unified(self, unified_data) -> Dict
```

### 2. OAuth Service

**Purpose**: Handle OAuth 2.0 authentication flow

**Flow**:

1. Generate authorization URL
2. Handle callback with authorization code
3. Exchange code for access token
4. Store encrypted tokens
5. Automatic token refresh

**Endpoints**:

```http
GET  /api/integrations/{crm_type}/authorize
GET  /api/integrations/{crm_type}/callback
POST /api/integrations/connections
GET  /api/integrations/connections
DELETE /api/integrations/connections/{id}
```

### 3. Sync Service

**Purpose**: Synchronize data between CRM and Miracle Birds

**Sync Types**:

- **Full Sync**: Initial complete data import
- **Incremental Sync**: Fetch only changed records
- **Real-time Sync**: Webhook-triggered instant updates

**Sync Pipeline**:

```
1. Fetch from CRM
2. Transform to unified schema
3. Detect changes (Create/Update/Delete)
4. Apply to database
5. Trigger AI predictions
6. Update sync status
```

**Endpoints**:

```http
POST /api/sync/start/{connection_id}?type=full|incremental
GET  /api/sync/status/{job_id}
GET  /api/sync/history/{connection_id}
```

### 4. Webhook Service

**Purpose**: Process real-time updates from CRM platforms

**Process**:

```
CRM Webhook → Verify Signature → Log Event → Queue Job → Process Async
```

**Endpoints**:

```http
POST /api/webhooks/salesforce
POST /api/webhooks/zoho
POST /api/webhooks/hubspot
POST /api/webhooks/dynamics
POST /api/webhooks/pipedrive
```

### 5. Token Manager

**Purpose**: Manage OAuth tokens with automatic refresh

**Features**:

- Token expiry checking
- Automatic token refresh
- Secure token storage (encrypted)
- Token rotation logging

### 6. Conflict Resolver

**Purpose**: Handle data conflicts between CRM and Miracle Birds

**Strategies**:

- `crm_wins` - CRM is source of truth (default)
- `mb_wins` - Miracle Birds data wins
- `newest_wins` - Most recent update wins
- `merge` - Merge non-conflicting fields

---

## API Endpoints

### Connection Management

#### Initiate OAuth Flow

```http
GET /api/integrations/{crm_type}/authorize
?redirect_uri=https://miraclebirds.ai/callback
&tenant_id={tenant_id}

Response: 302 Redirect to CRM authorization page
```

#### OAuth Callback

```http
GET /api/integrations/{crm_type}/callback
?code={authorization_code}
&state={state}

Response:
{
  "connection_id": "123",
  "crm_type": "salesforce",
  "status": "connected",
  "instance_url": "https://yourorg.salesforce.com"
}
```

#### List Connections

```http
GET /api/integrations/connections

Response:
{
  "connections": [
    {
      "id": "123",
      "crm_type": "salesforce",
      "status": "active",
      "created_at": "2026-07-13T10:00:00Z",
      "last_sync": "2026-07-13T20:00:00Z"
    }
  ]
}
```

#### Delete Connection

```http
DELETE /api/integrations/connections/{id}

Response:
{
  "success": true,
  "message": "Connection deleted successfully"
}
```

### Sync Management

#### Start Sync

```http
POST /api/sync/start/{connection_id}?type=full

Response:
{
  "job_id": "sync_789",
  "status": "running",
  "started_at": "2026-07-13T20:30:00Z",
  "estimated_duration": "30 minutes"
}
```

#### Check Sync Status

```http
GET /api/sync/status/{job_id}

Response:
{
  "job_id": "sync_789",
  "status": "completed",
  "records_synced": 5000,
  "records_created": 4500,
  "records_updated": 500,
  "errors": 0,
  "duration": "25 minutes"
}
```

---

## Configuration

```yaml
# CRM Integration Configuration

adapters:
  salesforce:
    client_id: ${SALESFORCE_CLIENT_ID}
    client_secret: ${SALESFORCE_CLIENT_SECRET}
    api_version: v58.0
    rate_limit: 15000 # per day

  zoho:
    client_id: ${ZOHO_CLIENT_ID}
    client_secret: ${ZOHO_CLIENT_SECRET}
    api_version: v3
    rate_limit: 5000 # per day

  hubspot:
    client_id: ${HUBSPOT_CLIENT_ID}
    client_secret: ${HUBSPOT_CLIENT_SECRET}
    api_version: v3
    rate_limit: 150 # per 10 seconds

sync:
  full_sync:
    enabled: true
    schedule: null # Manual trigger only

  incremental_sync:
    enabled: true
    schedule: "0 * * * *" # Every hour
    lookback_hours: 2

  webhooks:
    enabled: true
    verify_signature: true

rate_limiting:
  enabled: true
  strategy: token_bucket
  respect_crm_limits: true

conflict_resolution:
  default_strategy: crm_wins
  log_conflicts: true
```

---

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --port 8002

# Run Celery worker (for async sync jobs)
celery -A app.core.celery_app worker --loglevel=info

# Test OAuth flow
# 1. Navigate to: http://localhost:8002/api/integrations/salesforce/authorize
# 2. Complete OAuth in browser
# 3. Check connection status
```

---

## Data Flow

### Full Sync Flow

```
1. User clicks "Sync Now"
2. Create sync job in database
3. Celery picks up job
4. Authenticate with CRM
5. Fetch all records (paginated)
6. Transform to unified schema
7. Upsert into Miracle Birds DB
8. Trigger ML predictions for new customers
9. Update sync job status
10. Send completion notification
```

### Webhook Flow

```
1. User updates contact in Salesforce
2. Salesforce sends webhook to Miracle Birds
3. Verify webhook signature
4. Log webhook event
5. Queue webhook for processing
6. Celery worker processes webhook
7. Fetch full record from Salesforce
8. Transform and update in Miracle Birds
9. Trigger updated predictions
10. Log completion
```

---

## Error Handling

### Retry Logic

- **Transient errors**: Exponential backoff (5 attempts)
- **Rate limits**: Wait and retry
- **Permanent errors**: Log and alert, don't retry

### Error Logging

```json
{
  "error_id": "err_123",
  "connection_id": "conn_456",
  "error_type": "rate_limit_exceeded",
  "error_message": "Rate limit exceeded for Salesforce API",
  "timestamp": "2026-07-13T20:45:00Z",
  "retry_count": 3,
  "will_retry": true,
  "next_retry_at": "2026-07-13T20:46:00Z"
}
```

---

## Security

✅ **OAuth 2.0** for all CRM connections  
✅ **Encrypted token storage** (AES-256)  
✅ **Webhook signature verification**  
✅ **Rate limiting** to prevent abuse  
✅ **Audit logging** for all operations  
✅ **HTTPS only** communication  
✅ **Tenant isolation** (multi-tenant safe)

---

## Performance Targets

- **OAuth flow**: < 3 seconds
- **Full sync** (10K records): < 30 minutes
- **Incremental sync**: < 5 minutes
- **Webhook processing**: < 1 second
- **API response time**: < 200ms

---

## Monitoring

**Key Metrics**:

- Active connections count
- Sync jobs success rate
- Average sync duration
- Webhook processing time
- API error rate
- Rate limit utilization

**Alerts**:

- Sync job failures
- OAuth token refresh failures
- Rate limit exceeded
- Webhook signature verification failures
- Connection authentication errors

---

## Future Enhancements

🔮 **Additional CRM Platforms**:

- SAP Sales Cloud
- Oracle CRM
- SugarCRM
- Freshsales

🔮 **Advanced Features**:

- Custom field mapping UI
- Bi-directional field sync rules
- Conflict resolution UI
- Sync scheduling per connection
- Data transformation rules engine
- Real-time sync dashboard
- CRM activity timeline

---

## Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests (requires CRM sandbox)
pytest tests/integration/

# Test OAuth flow
python -m tests.test_oauth --crm=salesforce

# Test sync
python -m tests.test_sync --connection-id=123 --type=incremental
```

---

## Best Practices

1. **Always use OAuth 2.0** - Never store CRM passwords
2. **Respect rate limits** - Implement proper rate limiting
3. **Use incremental sync** - Don't fetch all data repeatedly
4. **Enable webhooks** - For real-time updates
5. **Log everything** - Comprehensive audit trail
6. **Handle errors gracefully** - Retry transient errors
7. **Test with sandbox** - Use CRM sandbox environments
8. **Monitor sync health** - Track success rates

---

**Version:** 1.0  
**Last Updated:** July 13, 2026  
**Maintained by:** Miracle Birds Engineering Team
