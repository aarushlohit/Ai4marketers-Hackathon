# 📡 Miracle Birds API Documentation

## Complete REST API Reference

**Version:** 1.0.0  
**Last Updated:** July 13, 2026  
**Base URL:** `https://api.miraclebirds.ai`

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Webhooks](#webhooks)
7. [SDKs & Libraries](#sdks--libraries)
8. [Best Practices](#best-practices)

---

## Getting Started

### Base URLs

```
Production:  https://api.miraclebirds.ai
Staging:     https://api-staging.miraclebirds.ai
Development: http://localhost:8000
```

### API Version

Current API version: **v1**

All endpoints are prefixed with `/api/v1/` unless otherwise noted.

### OpenAPI Specification

View the complete OpenAPI 3.0 specification:

- **Swagger UI**: https://api.miraclebirds.ai/docs
- **ReDoc**: https://api.miraclebirds.ai/redoc
- **OpenAPI YAML**: https://api.miraclebirds.ai/openapi.yaml

---

## Authentication

### Overview

Miracle Birds API uses **JWT (JSON Web Tokens)** for authentication.

### Authentication Flow

```
1. Register or Login → Get JWT tokens
2. Include access_token in Authorization header
3. Token expires after 30 minutes
4. Use refresh_token to get new access_token
```

### Obtaining Tokens

#### Register New User

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Acme Corp"
}

Response (201 Created):
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "user",
  "created_at": "2026-07-13T20:00:00Z"
}
```

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using the Access Token

Include the access token in the `Authorization` header for all API requests:

```http
GET /api/v1/customers
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Refreshing Tokens

When the access token expires, use the refresh token to obtain a new one:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## API Endpoints

### Customer Management

#### List Customers

```http
GET /api/v1/customers?page=1&page_size=50&status=active
Authorization: Bearer {token}

Response (200 OK):
{
  "customers": [
    {
      "id": "customer-uuid",
      "first_name": "Jane",
      "last_name": "Smith",
      "email": "jane@company.com",
      "company": "Tech Startup Inc",
      "status": "active",
      "crm_source": "salesforce",
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "total": 1500,
  "page": 1,
  "page_size": 50
}
```

**Query Parameters:**

- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 50, max: 100)
- `search` (string): Search by name or email
- `status` (enum): Filter by status (active, inactive, churned)
- `crm_source` (enum): Filter by CRM source

#### Get Customer Details

```http
GET /api/v1/customers/{customer_id}
Authorization: Bearer {token}

Response (200 OK):
{
  "id": "customer-uuid",
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@company.com",
  "phone": "+1234567890",
  "company": "Tech Startup Inc",
  "title": "CTO",
  "status": "active",
  "health_score": 85.5,
  "churn_risk": "low",
  "lead_score": 92,
  "lifetime_value": 25000.00,
  "interactions_count": 45,
  "created_at": "2026-01-15T10:30:00Z",
  "updated_at": "2026-07-13T15:20:00Z"
}
```

#### Customer 360 Intelligence

```http
GET /api/v1/customers/{customer_id}/360
Authorization: Bearer {token}

Response (200 OK):
{
  "customer": { /* customer details */ },
  "predictions": {
    "churn": {
      "churn_probability": 0.15,
      "risk_level": "low",
      "factors": [
        {"name": "engagement_score", "impact": 0.35},
        {"name": "support_tickets", "impact": 0.22}
      ]
    },
    "lead_score": {
      "score": 92,
      "grade": "A"
    },
    "revenue": {
      "predicted_revenue": 15000.00,
      "time_horizon_days": 90
    },
    "health_score": {
      "score": 85.5,
      "status": "excellent"
    }
  },
  "interactions": [ /* recent interactions */ ],
  "recommendations": [
    {
      "type": "upsell",
      "title": "Upgrade to Enterprise Plan",
      "priority": "high"
    }
  ]
}
```

#### Create Customer

```http
POST /api/v1/customers
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "phone": "+1234567890",
  "company": "Example Corp",
  "title": "VP of Sales"
}

Response (201 Created):
{
  "id": "new-customer-uuid",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  ...
}
```

#### Update Customer

```http
PUT /api/v1/customers/{customer_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "phone": "+9876543210",
  "title": "CEO"
}

Response (200 OK):
{ /* updated customer */ }
```

#### Delete Customer

```http
DELETE /api/v1/customers/{customer_id}
Authorization: Bearer {token}

Response (204 No Content)
```

---

### AI Predictions

#### Churn Prediction

```http
POST /api/v1/predictions/churn
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "customer-uuid"
}

Response (200 OK):
{
  "customer_id": "customer-uuid",
  "churn_probability": 0.72,
  "risk_level": "high",
  "factors": [
    {
      "name": "declining_engagement",
      "impact": 0.45
    },
    {
      "name": "support_tickets_increased",
      "impact": 0.30
    },
    {
      "name": "last_login_30_days_ago",
      "impact": 0.25
    }
  ],
  "predicted_churn_date": "2026-09-15",
  "confidence": 0.89
}
```

#### Lead Scoring

```http
POST /api/v1/predictions/lead-score
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "customer-uuid"
}

Response (200 OK):
{
  "customer_id": "customer-uuid",
  "score": 85,
  "grade": "A",
  "factors": [
    {"name": "company_size", "score": 25},
    {"name": "engagement_level", "score": 30},
    {"name": "intent_signals", "score": 20},
    {"name": "fit_score", "score": 10}
  ]
}
```

#### Revenue Prediction

```http
POST /api/v1/predictions/revenue
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "customer-uuid",
  "time_horizon": 90
}

Response (200 OK):
{
  "customer_id": "customer-uuid",
  "predicted_revenue": 15000.00,
  "time_horizon_days": 90,
  "confidence_interval": {
    "lower": 12000.00,
    "upper": 18000.00
  },
  "confidence": 0.85
}
```

#### Customer Health Score

```http
GET /api/v1/predictions/health-score/{customer_id}
Authorization: Bearer {token}

Response (200 OK):
{
  "customer_id": "customer-uuid",
  "score": 85.5,
  "status": "excellent",
  "factors": {
    "product_usage": 90,
    "engagement": 85,
    "support_satisfaction": 88,
    "payment_history": 95
  },
  "trend": "improving",
  "calculated_at": "2026-07-13T20:00:00Z"
}
```

---

### Analytics & Reporting

#### Dashboard Metrics

```http
GET /api/v1/analytics/dashboard?time_range=30d
Authorization: Bearer {token}

Response (200 OK):
{
  "total_customers": 1500,
  "active_customers": 1350,
  "at_risk_customers": 85,
  "churn_rate": 0.05,
  "avg_health_score": 82.3,
  "total_revenue": 450000.00,
  "predicted_revenue": 520000.00,
  "time_range": "30d",
  "calculated_at": "2026-07-13T20:00:00Z"
}
```

---

### CRM Integrations

#### Initiate OAuth Flow

```http
GET /api/v1/integrations/salesforce/authorize
Authorization: Bearer {token}

Response (200 OK):
{
  "authorization_url": "https://login.salesforce.com/services/oauth2/authorize?client_id=..."
}
```

After user authorization, Salesforce redirects to your callback URL with an authorization code.

#### List CRM Connections

```http
GET /api/v1/integrations/connections
Authorization: Bearer {token}

Response (200 OK):
{
  "connections": [
    {
      "id": "connection-uuid",
      "crm_type": "salesforce",
      "status": "active",
      "instance_url": "https://yourorg.salesforce.com",
      "last_sync": "2026-07-13T19:00:00Z",
      "created_at": "2026-07-01T10:00:00Z"
    }
  ]
}
```

#### Start Manual Sync

```http
POST /api/v1/integrations/sync/{connection_id}/start?sync_type=incremental
Authorization: Bearer {token}

Response (202 Accepted):
{
  "job_id": "sync-job-uuid",
  "connection_id": "connection-uuid",
  "sync_type": "incremental",
  "status": "pending",
  "started_at": "2026-07-13T20:30:00Z"
}
```

#### Delete CRM Connection

```http
DELETE /api/v1/integrations/connections/{connection_id}
Authorization: Bearer {token}

Response (204 No Content)
```

---

### AI Copilot

#### Chat with Copilot

```http
POST /api/v1/copilot/chat
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "Show me customers at high risk of churning",
  "context": {
    "view": "dashboard"
  }
}

Response (200 OK):
{
  "message": "I found 12 customers at high risk of churning. Here are the top 5:\n\n1. Acme Corp (85% churn probability)\n2. Tech Startup Inc (78% churn probability)\n...",
  "conversation_id": "conversation-uuid",
  "suggestions": [
    "Show me details for Acme Corp",
    "What actions can reduce churn risk?",
    "Schedule retention calls"
  ],
  "data": {
    "customers": [ /* customer list */ ]
  }
}
```

#### List Conversations

```http
GET /api/v1/copilot/conversations
Authorization: Bearer {token}

Response (200 OK):
{
  "conversations": [
    {
      "id": "conversation-uuid",
      "title": "Churn risk analysis",
      "created_at": "2026-07-13T15:00:00Z",
      "messages_count": 8,
      "last_message_at": "2026-07-13T15:45:00Z"
    }
  ]
}
```

---

### User Management

#### Get Current User Profile

```http
GET /api/v1/users/me
Authorization: Bearer {token}

Response (200 OK):
{
  "id": "user-uuid",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "admin",
  "tenant_id": "tenant-uuid",
  "phone": "+1234567890",
  "created_at": "2026-06-01T10:00:00Z",
  "last_login": "2026-07-13T19:30:00Z"
}
```

#### Update User Profile

```http
PUT /api/v1/users/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "first_name": "Jonathan",
  "phone": "+9876543210"
}

Response (200 OK):
{ /* updated user */ }
```

---

### Workflows

#### List Workflows

```http
GET /api/v1/workflows
Authorization: Bearer {token}

Response (200 OK):
{
  "workflows": [
    {
      "id": "workflow-uuid",
      "name": "High Churn Risk Alert",
      "description": "Send email when customer churn risk exceeds 70%",
      "status": "active",
      "trigger_type": "prediction_threshold",
      "actions_count": 2,
      "executions_count": 145,
      "created_at": "2026-06-15T10:00:00Z"
    }
  ]
}
```

---

## Error Handling

### HTTP Status Codes

```
200 OK               - Request successful
201 Created          - Resource created successfully
202 Accepted         - Request accepted for processing
204 No Content       - Request successful, no content to return
400 Bad Request      - Invalid request parameters
401 Unauthorized     - Authentication required or failed
403 Forbidden        - Insufficient permissions
404 Not Found        - Resource not found
409 Conflict         - Resource conflict (e.g., duplicate email)
422 Unprocessable Entity - Validation error
429 Too Many Requests - Rate limit exceeded
500 Internal Server Error - Server error
503 Service Unavailable - Service temporarily unavailable
```

### Error Response Format

```json
{
  "error": "validation_error",
  "detail": "Email is required",
  "code": "VALIDATION_ERROR",
  "timestamp": "2026-07-13T20:00:00Z",
  "path": "/api/v1/auth/register"
}
```

### Common Error Codes

```
VALIDATION_ERROR          - Input validation failed
AUTHENTICATION_FAILED     - Invalid credentials
TOKEN_EXPIRED            - JWT token expired
PERMISSION_DENIED        - Insufficient permissions
RESOURCE_NOT_FOUND       - Requested resource not found
RATE_LIMIT_EXCEEDED      - Too many requests
DUPLICATE_RESOURCE       - Resource already exists
INTEGRATION_ERROR        - CRM integration error
PREDICTION_FAILED        - ML prediction failed
```

---

## Rate Limiting

### Rate Limits by Plan

```
Standard Plan:     1,000 requests/hour
Professional Plan: 5,000 requests/hour
Enterprise Plan:   Unlimited
```

### Rate Limit Headers

Every API response includes rate limit information:

```http
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4892
X-RateLimit-Reset: 1689282000
```

### Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1689282000
Retry-After: 120

{
  "error": "rate_limit_exceeded",
  "detail": "You have exceeded your rate limit. Please try again in 120 seconds.",
  "code": "RATE_LIMIT_EXCEEDED"
}
```

---

## Webhooks

Miracle Birds can send webhooks to notify your application of important events.

### Available Webhook Events

```
customer.created         - New customer created
customer.updated         - Customer information updated
customer.deleted         - Customer deleted
prediction.completed     - Prediction calculation completed
churn.risk_high          - Customer churn risk is high
lead.score_updated       - Lead score changed significantly
sync.completed           - CRM sync completed
sync.failed              - CRM sync failed
workflow.executed        - Workflow executed
```

### Webhook Payload Example

```json
{
  "event": "churn.risk_high",
  "timestamp": "2026-07-13T20:00:00Z",
  "data": {
    "customer_id": "customer-uuid",
    "churn_probability": 0.85,
    "risk_level": "high"
  },
  "tenant_id": "tenant-uuid",
  "webhook_id": "webhook-event-uuid"
}
```

### Webhook Signature Verification

All webhooks include an `X-Webhook-Signature` header for verification:

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## SDKs & Libraries

### Official SDKs

```
Python SDK:     pip install miraclebirds
JavaScript SDK: npm install @miraclebirds/sdk
Ruby SDK:       gem install miraclebirds
Go SDK:         go get github.com/miraclebirds/go-sdk
```

### Python SDK Example

```python
from miraclebirds import MiracleBirds

# Initialize client
client = MiracleBirds(api_key="your_api_key")

# Get customers
customers = client.customers.list(status="active", page_size=50)

# Get customer 360 view
customer_360 = client.customers.get_360(customer_id="customer-uuid")

# Predict churn
churn_prediction = client.predictions.churn(customer_id="customer-uuid")

# Chat with copilot
response = client.copilot.chat(message="Show me at-risk customers")
```

### JavaScript SDK Example

```javascript
import { MiracleBirds } from "@miraclebirds/sdk";

// Initialize client
const client = new MiracleBirds({ apiKey: "your_api_key" });

// Get customers
const customers = await client.customers.list({
  status: "active",
  pageSize: 50,
});

// Get customer 360 view
const customer360 = await client.customers.get360("customer-uuid");

// Predict churn
const churnPrediction = await client.predictions.churn("customer-uuid");

// Chat with copilot
const response = await client.copilot.chat("Show me at-risk customers");
```

---

## Best Practices

### 1. Authentication

✅ **DO:**

- Store tokens securely
- Implement automatic token refresh
- Use HTTPS only

❌ **DON'T:**

- Store tokens in localStorage (use httpOnly cookies or secure storage)
- Share tokens between users
- Hardcode tokens in source code

### 2. Error Handling

✅ **DO:**

- Implement exponential backoff for retries
- Handle rate limits gracefully
- Log errors for debugging

❌ **DON'T:**

- Ignore error responses
- Retry indefinitely
- Expose error details to end users

### 3. Performance

✅ **DO:**

- Use pagination for large result sets
- Cache responses when appropriate
- Implement request debouncing

❌ **DON'T:**

- Fetch all records at once
- Make unnecessary API calls
- Ignore rate limits

### 4. Security

✅ **DO:**

- Validate webhook signatures
- Use environment variables for secrets
- Implement request timeouts

❌ **DON'T:**

- Trust user input blindly
- Expose API keys in client-side code
- Disable SSL certificate verification

---

## Support

### Resources

- **API Documentation**: https://api.miraclebirds.ai/docs
- **Developer Portal**: https://developers.miraclebirds.ai
- **Status Page**: https://status.miraclebirds.ai
- **GitHub Issues**: https://github.com/miraclebirds/issues

### Contact

- **Email**: api-support@miraclebirds.ai
- **Slack Community**: https://miraclebirds.slack.com
- **Support Portal**: https://support.miraclebirds.ai

---

**Version:** 1.0.0  
**Last Updated:** July 13, 2026  
**© 2026 Miracle Birds. All rights reserved.**
