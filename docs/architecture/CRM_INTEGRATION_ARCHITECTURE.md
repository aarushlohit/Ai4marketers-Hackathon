# 🔗 CRM Integration Architecture

## Miracle Birds - Unified CRM Integration Layer

**Version:** 1.0  
**Last Updated:** July 13, 2026  
**Purpose:** Enterprise-grade CRM integration architecture specification

---

## Table of Contents

1. [Integration Overview](#integration-overview)
2. [Supported CRM Platforms](#supported-crm-platforms)
3. [Architecture Pattern](#architecture-pattern)
4. [OAuth Authentication](#oauth-authentication)
5. [Data Synchronization](#data-synchronization)
6. [Webhook Processing](#webhook-processing)
7. [Error Handling & Retry](#error-handling--retry)
8. [Rate Limiting](#rate-limiting)

---

## Integration Overview

### Core Philosophy

**Miracle Birds is NOT a CRM replacement**  
It is an **AI Intelligence Layer** that enhances existing CRM systems.

```
┌─────────────────────────────────────────────────┐
│           Miracle Birds Philosophy              │
├─────────────────────────────────────────────────┤
│ ✓ We DON'T replace your CRM                    │
│ ✓ We ADD intelligence to your CRM data         │
│ ✓ We SYNC bi-directionally with your CRM       │
│ ✓ We RESPECT your CRM as source of truth       │
│ ✓ We ENHANCE with AI predictions & insights    │
└─────────────────────────────────────────────────┘
```

### Integration Capabilities

- **Unified API**: Single interface for multiple CRM platforms
- **Bi-directional Sync**: Read and write data seamlessly
- **Real-time Updates**: Webhook-based instant synchronization
- **Data Mapping**: Transform CRM-specific formats to unified schema
- **OAuth Security**: Enterprise-grade authentication
- **Conflict Resolution**: Intelligent data conflict handling
- **Rate Limit Compliance**: Respect CRM API quotas

---

## Supported CRM Platforms

### 1️⃣ Salesforce

```yaml
Platform: Salesforce
API Version: REST API v58.0
Authentication: OAuth 2.0
Rate Limits: 15,000 calls/24h (varies by edition)

Supported Objects:
  - Account (Companies)
  - Contact (People)
  - Lead (Prospects)
  - Opportunity (Deals)
  - Case (Support tickets)
  - Task & Event (Activities)

Features: ✓ Real-time webhooks via Platform Events
  ✓ SOQL queries for data retrieval
  ✓ Bulk API for large data transfers
  ✓ Metadata API for schema discovery
  ✓ Custom objects support

OAuth Scopes Required:
  - full (full access to user's data)
  - api (API integration access)
  - refresh_token (offline access)
```

### 2️⃣ Zoho CRM

```yaml
Platform: Zoho CRM
API Version: v3
Authentication: OAuth 2.0
Rate Limits: 5,000 calls/day (varies by edition)

Supported Modules:
  - Accounts
  - Contacts
  - Leads
  - Deals
  - Cases
  - Tasks & Events

Features: ✓ Webhooks for instant notifications
  ✓ COQL (Zoho Query Language)
  ✓ Bulk API operations
  ✓ Custom module support
  ✓ Blueprint workflows

OAuth Scopes Required:
  - ZohoCRM.modules.ALL
  - ZohoCRM.settings.ALL
  - ZohoCRM.notifications.ALL
```

### 3️⃣ HubSpot

```yaml
Platform: HubSpot
API Version: v3
Authentication: OAuth 2.0
Rate Limits: 150 requests/10 seconds

Supported Objects:
  - Contacts
  - Companies
  - Deals
  - Tickets
  - Tasks
  - Meetings

Features: ✓ Webhooks for property changes
  ✓ Search API with filters
  ✓ Batch operations (up to 100 records)
  ✓ Custom properties support
  ✓ Associations between objects

OAuth Scopes Required:
  - crm.objects.contacts.read/write
  - crm.objects.companies.read/write
  - crm.objects.deals.read/write
```

### 4️⃣ Microsoft Dynamics 365

```yaml
Platform: Microsoft Dynamics 365
API Version: Web API v9.2
Authentication: OAuth 2.0 (Azure AD)
Rate Limits: 20,000 calls/user/5 minutes

Supported Entities:
  - Account
  - Contact
  - Lead
  - Opportunity
  - Incident (Case)
  - Task & Appointment

Features: ✓ Webhooks via Service Bus
  ✓ FetchXML for complex queries
  ✓ OData batch operations
  ✓ Custom entities support
  ✓ Business process flows

OAuth Scopes Required:
  - https://org.crm.dynamics.com/user_impersonation
```

### 5️⃣ Pipedrive

```yaml
Platform: Pipedrive
API Version: v1
Authentication: OAuth 2.0 + API Key
Rate Limits: 2 requests/second per company

Supported Resources:
  - Organizations
  - Persons
  - Deals
  - Activities
  - Notes
  - Products

Features: ✓ Webhooks for entity changes
  ✓ Search endpoints
  ✓ Batch updates
  ✓ Custom fields
  ✓ Pipeline management

OAuth Scopes Required:
  - admin (full access)
```

---

## Architecture Pattern

### Adapter Pattern Implementation

```
┌────────────────────────────────────────────────────────┐
│         Miracle Birds - CRM Integration Layer          │
└────────────────────────────────────────────────────────┘
                          │
                [Unified CRM API]
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
[Adapter Interface]  [Data Mapper]  [Sync Engine]
        │                 │                 │
  ┌─────┴─────┬──────┬────┴────┬──────┐    │
  │           │      │         │      │    │
[Salesforce][Zoho][HubSpot][Dynamics][Pipedrive]
  │           │      │         │      │
[SF API]  [Zoho API][HS API][D365 API][PD API]
```

### Base Adapter Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class CRMAdapter(ABC):
    """Base adapter for all CRM integrations"""

    def __init__(self, credentials: Dict[str, str]):
        self.credentials = credentials
        self.client = None

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with CRM platform"""
        pass

    @abstractmethod
    async def get_contacts(
        self,
        filters: Optional[Dict] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve contacts from CRM"""
        pass

    @abstractmethod
    async def create_contact(
        self,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new contact in CRM"""
        pass

    @abstractmethod
    async def update_contact(
        self,
        contact_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing contact"""
        pass

    @abstractmethod
    async def get_accounts(
        self,
        filters: Optional[Dict] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve accounts/companies"""
        pass

    @abstractmethod
    async def handle_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process webhook from CRM"""
        pass

    @abstractmethod
    def map_to_unified(self, crm_data: Dict) -> Dict:
        """Map CRM data to unified schema"""
        pass

    @abstractmethod
    def map_from_unified(self, unified_data: Dict) -> Dict:
        """Map unified schema to CRM format"""
        pass
```

### Unified Data Schema

```json
{
  "customer": {
    "id": "uuid",
    "external_id": "crm_record_id",
    "crm_source": "salesforce|zoho|hubspot|dynamics|pipedrive",
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "phone": "string",
    "company": "string",
    "title": "string",
    "status": "active|inactive",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "attributes": {
      "custom_field_1": "value",
      "crm_specific_data": {}
    }
  }
}
```

---

## OAuth Authentication

### OAuth 2.0 Authorization Flow

```
┌──────────────────────────────────────────────────────┐
│     OAuth 2.0 Authorization Code Flow                │
└──────────────────────────────────────────────────────┘

Step 1: User Initiates Connection
   └─ Click "Connect Salesforce" button

Step 2: Redirect to CRM Authorization
   ├─ URL: https://login.salesforce.com/oauth2/authorize
   ├─ client_id: {your_client_id}
   ├─ redirect_uri: https://miraclebirds.ai/callback
   ├─ response_type: code
   └─ scope: full api refresh_token

Step 3: User Grants Permission
   └─ Logs into CRM and authorizes

Step 4: CRM Redirects with Code
   └─ https://miraclebirds.ai/callback?code=ABC123

Step 5: Exchange Code for Tokens
   ├─ POST: /oauth2/token
   ├─ grant_type: authorization_code
   ├─ code: ABC123
   └─ client_secret: {secret}

Step 6: Store Tokens Securely
   ├─ access_token (encrypted)
   ├─ refresh_token (encrypted)
   ├─ expires_at
   └─ Store in database

Step 7: Test Connection
   └─ Make test API call

Step 8: Start Initial Sync
   └─ Trigger full data synchronization
```

### Token Management

```python
class TokenManager:
    """Manage OAuth tokens with auto-refresh"""

    async def get_valid_token(self, connection_id: int) -> str:
        """Get valid token, refresh if expired"""
        connection = await self.get_connection(connection_id)

        if self.is_token_expired(connection):
            await self.refresh_token(connection)
            connection = await self.get_connection(connection_id)

        return connection.access_token

    async def refresh_token(self, connection):
        """Refresh access token"""
        adapter = self.get_adapter(connection.crm_type)

        new_tokens = await adapter.refresh_access_token(
            refresh_token=connection.refresh_token
        )

        await self.update_connection(
            connection.id,
            access_token=new_tokens['access_token'],
            expires_at=datetime.now() + timedelta(
                seconds=new_tokens['expires_in']
            )
        )
```

---

## Data Synchronization

### Sync Strategies

```
┌──────────────────────────────────────────────────┐
│            Three Sync Strategies                 │
├──────────────────────────────────────────────────┤
│                                                  │
│ 1. FULL SYNC (Initial)                          │
│    ├─ When: After connection setup              │
│    ├─ Fetches: All CRM records                  │
│    ├─ Duration: 30 min - 2 hours                │
│    └─ Frequency: Once                           │
│                                                  │
│ 2. INCREMENTAL SYNC (Scheduled)                 │
│    ├─ When: Every hour (configurable)           │
│    ├─ Fetches: Only changed records             │
│    ├─ Filter: LastModifiedDate                  │
│    ├─ Duration: 1-5 minutes                     │
│    └─ Frequency: Hourly/Daily                   │
│                                                  │
│ 3. REAL-TIME SYNC (Webhooks)                    │
│    ├─ When: Instant on CRM change               │
│    ├─ Fetches: Single changed record            │
│    ├─ Duration: < 1 second                      │
│    └─ Frequency: On event                       │
└──────────────────────────────────────────────────┘
```

### Sync Pipeline

```python
async def sync_pipeline(connection_id: int, sync_type: str):
    """
    Synchronization pipeline

    Steps:
    1. Fetch data from CRM
    2. Transform to unified schema
    3. Detect changes (Create/Update/Delete)
    4. Apply changes to database
    5. Trigger AI predictions
    6. Update sync status
    """

    # 1. Fetch from CRM
    adapter = get_adapter(connection_id)
    await adapter.authenticate()

    if sync_type == 'full':
        crm_records = await adapter.get_all_contacts()
    else:
        last_sync = await get_last_sync_time(connection_id)
        crm_records = await adapter.get_contacts(
            filters={'updated_since': last_sync}
        )

    # 2. Transform data
    unified_records = [
        adapter.map_to_unified(record)
        for record in crm_records
    ]

    # 3. Detect changes
    changes = await detect_changes(unified_records)

    # 4. Apply changes
    for change in changes:
        if change['action'] == 'create':
            await create_customer(change['data'])
        elif change['action'] == 'update':
            await update_customer(change['id'], change['data'])
        elif change['action'] == 'delete':
            await soft_delete_customer(change['id'])

    # 5. Trigger predictions
    await trigger_predictions(changes)

    # 6. Update sync status
    await update_sync_status(connection_id, {
        'last_sync': datetime.now(),
        'records_synced': len(changes),
        'status': 'completed'
    })
```

### Conflict Resolution

```python
class ConflictResolver:
    """Resolve data conflicts"""

    def resolve(
        self,
        crm_record: Dict,
        mb_record: Dict,
        strategy: str = 'crm_wins'
    ) -> Dict:
        """
        Conflict resolution strategies:
        - crm_wins: CRM is source of truth (default)
        - mb_wins: Miracle Birds wins
        - newest_wins: Most recent update wins
        - merge: Merge non-conflicting fields
        """

        if strategy == 'crm_wins':
            return crm_record

        elif strategy == 'newest_wins':
            crm_time = crm_record.get('updated_at')
            mb_time = mb_record.get('updated_at')
            return crm_record if crm_time > mb_time else mb_record

        elif strategy == 'merge':
            merged = crm_record.copy()
            for key, value in mb_record.items():
                if key not in merged or merged[key] is None:
                    merged[key] = value
            return merged

        return crm_record
```

---

## Webhook Processing

### Webhook Architecture

```
CRM Platform
    │
    │ (Webhook Event)
    ↓
[Load Balancer]
    ↓
[Webhook Endpoint]
    ├─ Verify signature
    ├─ Log event
    └─ Queue for processing
        ↓
[Redis Queue]
        ↓
[Celery Worker]
    ├─ Parse event
    ├─ Fetch full record
    ├─ Transform data
    ├─ Update database
    └─ Trigger AI
```

### Webhook Endpoint

```python
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.post("/webhooks/{crm_type}")
async def handle_webhook(crm_type: str, request: Request):
    """
    Handle incoming CRM webhooks

    Supported: salesforce, zoho, hubspot, dynamics, pipedrive
    """

    payload = await request.json()
    headers = dict(request.headers)

    # Verify signature
    webhook_service = WebhookService()
    if not webhook_service.verify_signature(
        crm_type, payload, headers
    ):
        raise HTTPException(401, "Invalid signature")

    # Log webhook
    await webhook_service.log_webhook(crm_type, payload)

    # Queue for async processing
    await webhook_service.queue_webhook(crm_type, payload)

    return {"status": "accepted"}
```

---

## Error Handling & Retry

### Retry Logic

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class CRMAPIClient:
    @retry(
        retry=retry_if_exception_type(
            (TimeoutError, ConnectionError)
        ),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    async def make_api_call(self, endpoint: str, **kwargs):
        """
        API call with exponential backoff

        Retry Schedule:
        - Attempt 1: Immediate
        - Attempt 2: Wait 4s
        - Attempt 3: Wait 8s
        - Attempt 4: Wait 16s
        - Attempt 5: Wait 32s
        - After 5 attempts: Raise exception
        """
        response = await self.client.request(endpoint, **kwargs)
        response.raise_for_status()
        return response.json()
```

### Error Classification

```
┌─────────────────────────────────────────────────┐
│            Error Handling Strategy              │
├─────────────────────────────────────────────────┤
│                                                 │
│ TRANSIENT ERRORS (Retry):                      │
│ ├─ Network timeout                             │
│ ├─ Rate limit exceeded (wait & retry)          │
│ ├─ Service unavailable (503)                   │
│ └─ Temporary auth issues                       │
│                                                 │
│ PERMANENT ERRORS (Don't Retry):                │
│ ├─ Invalid credentials (401)                   │
│ ├─ Permission denied (403)                     │
│ ├─ Resource not found (404)                    │
│ ├─ Invalid request (400)                       │
│ └─ CRM record deleted                          │
│                                                 │
│ BUSINESS LOGIC ERRORS:                         │
│ ├─ Validation failures                         │
│ ├─ Duplicate records                           │
│ ├─ Conflict resolution needed                  │
│ └─ Data quality issues                         │
└─────────────────────────────────────────────────┘
```

---

## Rate Limiting

### CRM Rate Limits

```yaml
Salesforce:
  requests_per_day: 15000
  requests_per_second: 20

Zoho CRM:
  requests_per_day: 5000
  requests_per_minute: 100

HubSpot:
  requests_per_10_seconds: 150

Dynamics 365:
  requests_per_5_minutes: 20000

Pipedrive:
  requests_per_second: 2
```

### Rate Limiter Implementation

```python
class RateLimiter:
    """Manage CRM API rate limits"""

    def __init__(self, crm_type: str):
        self.crm_type = crm_type
        self.limits = self.get_limits(crm_type)
        self.redis = Redis()

    async def check_rate_limit(self, connection_id: int) -> bool:
        """Check if request allowed"""
        key = f"rate:{self.crm_type}:{connection_id}"
        current = await self.redis.get(key)

        if current and int(current) >= self.limits['per_day']:
            return False

        await self.redis.incr(key)
        await self.redis.expire(key, 86400)
        return True

    async def wait_if_needed(self, connection_id: int):
        """Wait if rate limit exceeded"""
        while not await self.check_rate_limit(connection_id):
            await asyncio.sleep(60)
```

---

## Summary

✅ **Unified Interface** for 5 major CRM platforms  
✅ **Secure OAuth 2.0** authentication  
✅ **Bi-directional Sync** (read & write)  
✅ **Real-time Webhooks** for instant updates  
✅ **Smart Conflict Resolution**  
✅ **Automatic Retry Logic**  
✅ **Rate Limit Compliance**  
✅ **Extensible Adapter Pattern**

---

**Version:** 1.0  
**Last Updated:** July 13, 2026  
**Next Review:** October 13, 2026
