# 🗄️ Miracle Birds - Database Schema Design

## PostgreSQL Database Architecture with pgvector

**Document Version:** 1.0  
**Last Updated:** July 13, 2026  
**Database:** PostgreSQL 16 with pgvector extension

---

## Table of Contents

1. [Database Overview](#database-overview)
2. [Multi-Tenant Strategy](#multi-tenant-strategy)
3. [Core Schema](#core-schema)
4. [Entity Relationship Diagrams](#entity-relationship-diagrams)
5. [Table Definitions](#table-definitions)
6. [Vector Database Design](#vector-database-design)
7. [Indexing Strategy](#indexing-strategy)
8. [Partitioning Strategy](#partitioning-strategy)
9. [Security & Access Control](#security--access-control)
10. [Migration Strategy](#migration-strategy)

---

## Database Overview

### Design Principles

✅ **Multi-Tenancy**: Row-Level Security (RLS) for tenant isolation  
✅ **Scalability**: Partitioning for large tables  
✅ **Performance**: Strategic indexing and materialized views  
✅ **Security**: Encryption, RLS policies, audit trails  
✅ **Consistency**: Foreign keys and constraints  
✅ **Flexibility**: JSONB for dynamic attributes  
✅ **AI-Ready**: Vector embeddings with pgvector

### Database Statistics

```
Estimated Table Sizes (per tenant with 10K customers):
├─ customers: ~1M rows, ~500MB
├─ predictions: ~10M rows, ~2GB
├─ customer_interactions: ~100M rows, ~20GB
├─ embeddings: ~500K rows, ~2GB (with vectors)
├─ audit_logs: ~50M rows, ~10GB
└─ Total: ~35GB per tenant
```

---

## Multi-Tenant Strategy

### Row-Level Security (RLS)

Every table includes a `tenant_id` column with RLS policies to ensure complete data isolation.

```sql
-- Enable RLS on a table
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Create policy for tenant isolation
CREATE POLICY tenant_isolation_policy ON customers
    USING (tenant_id = current_setting('app.current_tenant_id')::bigint);

-- Create policy for insert
CREATE POLICY tenant_isolation_insert ON customers
    FOR INSERT
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id')::bigint);
```

### Setting Tenant Context

```sql
-- Set tenant context at session start
SET app.current_tenant_id = '123';

-- All queries automatically filtered by tenant_id
SELECT * FROM customers;  -- Only returns tenant 123's data
```

---

## Core Schema

### Database Modules

```
miracle_birds_db/
├── core/                    # Core business entities
│   ├── tenants
│   ├── users
│   ├── roles
│   ├── permissions
│   └── user_roles
├── customers/               # Customer data
│   ├── customers
│   ├── customer_contacts
│   ├── customer_interactions
│   ├── customer_segments
│   └── customer_tags
├── predictions/             # ML predictions
│   ├── churn_predictions
│   ├── lead_scores
│   ├── revenue_predictions
│   ├── clv_predictions
│   └── health_scores
├── integrations/            # CRM integrations
│   ├── crm_connections
│   ├── crm_sync_jobs
│   ├── crm_field_mappings
│   └── webhook_events
├── ai/                      # AI & embeddings
│   ├── conversations
│   ├── messages
│   ├── embeddings
│   └── ai_actions
├── workflows/               # Automation
│   ├── workflow_definitions
│   ├── workflow_executions
│   ├── workflow_tasks
│   └── workflow_triggers
├── analytics/               # Analytics & metrics
│   ├── customer_metrics
│   ├── engagement_metrics
│   └── business_metrics
├── security/                # Security & compliance
│   ├── audit_logs
│   ├── pii_detections
│   ├── security_events
│   └── api_keys
└── system/                  # System tables
    ├── feature_flags
    ├── notifications
    └── system_events
```

---

## Entity Relationship Diagrams

### Core Entities ER Diagram

```
┌─────────────────┐
│    tenants      │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐         ┌──────────────────┐
│     users       │────────►│   user_roles     │
└────────┬────────┘ 1     N └────────┬─────────┘
         │                           │
         │ 1                         │ N
         │                    ┌──────▼──────┐
         │ N                  │    roles    │
┌────────▼────────┐           └─────────────┘
│   customers     │
└────────┬────────┘
         │ 1
         │
         ├────────────────┬────────────────┬
         │ N              │ N              │ N
┌────────▼────────┐ ┌─────▼─────┐  ┌──────▼──────┐
│customer_contacts│ │interactions│  │customer_tags│
└─────────────────┘ └────────────┘  └─────────────┘
```
