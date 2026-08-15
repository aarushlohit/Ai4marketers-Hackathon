-- ============================================================
-- Miracle Birds — PostgreSQL 16 Database Initialisation
-- Run once on a fresh database instance.
-- Requires: pgvector extension
-- ============================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ============================================================
-- SCHEMAS
-- ============================================================
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS customers;
CREATE SCHEMA IF NOT EXISTS predictions;
CREATE SCHEMA IF NOT EXISTS integrations;
CREATE SCHEMA IF NOT EXISTS ai;
CREATE SCHEMA IF NOT EXISTS workflows;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS security;

-- ============================================================
-- CORE SCHEMA — tenants, users, roles
-- ============================================================

CREATE TABLE IF NOT EXISTS core.tenants (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    plan            VARCHAR(50)  NOT NULL DEFAULT 'standard',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    settings        JSONB                 DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core.users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    hashed_password TEXT         NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    role            VARCHAR(50)  NOT NULL DEFAULT 'user',
    phone           VARCHAR(50),
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    is_verified     BOOLEAN      NOT NULL DEFAULT FALSE,
    mfa_enabled     BOOLEAN      NOT NULL DEFAULT FALSE,
    mfa_secret      TEXT,
    last_login      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_tenant_id ON core.users(tenant_id);
CREATE INDEX IF NOT EXISTS ix_users_email     ON core.users(email);

-- ============================================================
-- CUSTOMERS SCHEMA
-- ============================================================

CREATE TABLE IF NOT EXISTS customers.customers (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id           UUID         NOT NULL,
    external_id         VARCHAR(255),
    crm_source          VARCHAR(50),
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    email               VARCHAR(255),
    phone               VARCHAR(50),
    company             VARCHAR(255),
    title               VARCHAR(100),
    status              VARCHAR(50)  NOT NULL DEFAULT 'active',
    -- Cached AI/ML scores (refreshed by ML engine)
    health_score        FLOAT,
    churn_probability   FLOAT,
    lead_score          INTEGER,
    lifetime_value      FLOAT,
    attributes          JSONB                 DEFAULT '{}',
    is_deleted          BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_customers_tenant_external
    ON customers.customers(tenant_id, external_id, crm_source)
    WHERE external_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_customers_tenant_status
    ON customers.customers(tenant_id, status)
    WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS ix_customers_tenant_email
    ON customers.customers(tenant_id, email)
    WHERE email IS NOT NULL;

-- GIN index for full-text search on name + company
CREATE INDEX IF NOT EXISTS ix_customers_search
    ON customers.customers
    USING gin(to_tsvector('english',
        coalesce(first_name,'') || ' ' ||
        coalesce(last_name,'')  || ' ' ||
        coalesce(email,'')      || ' ' ||
        coalesce(company,'')));

CREATE TABLE IF NOT EXISTS customers.customer_interactions (
    id              UUID NOT NULL DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    customer_id     UUID         NOT NULL REFERENCES customers.customers(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL,
    subject         TEXT,
    body            TEXT,
    sentiment_score FLOAT,
    occurred_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, occurred_at)            -- must include partition key
) PARTITION BY RANGE (occurred_at);

-- Monthly partitions for 2026
CREATE TABLE IF NOT EXISTS customers.customer_interactions_2026_07
    PARTITION OF customers.customer_interactions
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');

CREATE TABLE IF NOT EXISTS customers.customer_interactions_2026_08
    PARTITION OF customers.customer_interactions
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

CREATE INDEX IF NOT EXISTS ix_interactions_customer
    ON customers.customer_interactions(customer_id, occurred_at DESC);

-- ============================================================
-- PREDICTIONS SCHEMA
-- ============================================================

CREATE TABLE IF NOT EXISTS predictions.churn_predictions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id           UUID    NOT NULL,
    customer_id         UUID    NOT NULL REFERENCES customers.customers(id) ON DELETE CASCADE,
    churn_probability   FLOAT   NOT NULL,
    risk_level          VARCHAR(20) NOT NULL, -- low | medium | high
    factors             JSONB   NOT NULL DEFAULT '[]',
    confidence          FLOAT,
    model_version       VARCHAR(50),
    predicted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_churn_customer_latest
    ON predictions.churn_predictions(customer_id, predicted_at DESC);

CREATE TABLE IF NOT EXISTS predictions.lead_scores (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID    NOT NULL,
    customer_id     UUID    NOT NULL REFERENCES customers.customers(id) ON DELETE CASCADE,
    score           INTEGER NOT NULL,
    grade           CHAR(1) NOT NULL,
    factors         JSONB   NOT NULL DEFAULT '[]',
    model_version   VARCHAR(50),
    scored_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predictions.health_scores (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID    NOT NULL,
    customer_id     UUID    NOT NULL REFERENCES customers.customers(id) ON DELETE CASCADE,
    score           FLOAT   NOT NULL,
    status          VARCHAR(20) NOT NULL, -- excellent|good|fair|poor|critical
    factors         JSONB   NOT NULL DEFAULT '{}',
    trend           VARCHAR(20),
    calculated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- INTEGRATIONS SCHEMA
-- ============================================================

CREATE TABLE IF NOT EXISTS integrations.crm_connections (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    crm_type        VARCHAR(50)  NOT NULL, -- salesforce|zoho|hubspot|dynamics|pipedrive
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    access_token    TEXT,        -- encrypted at application layer
    refresh_token   TEXT,        -- encrypted at application layer
    token_expires_at TIMESTAMPTZ,
    instance_url    TEXT,
    last_sync_at    TIMESTAMPTZ,
    sync_config     JSONB        DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_connections_tenant_crm
    ON integrations.crm_connections(tenant_id, crm_type);

CREATE TABLE IF NOT EXISTS integrations.sync_jobs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    connection_id   UUID         NOT NULL REFERENCES integrations.crm_connections(id),
    sync_type       VARCHAR(20)  NOT NULL, -- full | incremental
    status          VARCHAR(20)  NOT NULL DEFAULT 'pending',
    records_synced  INTEGER      DEFAULT 0,
    errors          INTEGER      DEFAULT 0,
    started_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    error_details   JSONB
);

CREATE TABLE IF NOT EXISTS integrations.webhook_events (
    id              UUID NOT NULL DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    connection_id   UUID,
    crm_type        VARCHAR(50)  NOT NULL,
    event_type      VARCHAR(100) NOT NULL,
    raw_payload     JSONB        NOT NULL,
    processed       BOOLEAN      NOT NULL DEFAULT FALSE,
    received_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, received_at)            -- must include partition key
) PARTITION BY RANGE (received_at);

CREATE TABLE IF NOT EXISTS integrations.webhook_events_2026_07
    PARTITION OF integrations.webhook_events
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');

-- ============================================================
-- AI SCHEMA — conversations, embeddings
-- ============================================================

CREATE TABLE IF NOT EXISTS ai.conversations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    user_id         UUID         NOT NULL,
    title           VARCHAR(255),
    message_count   INTEGER      NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_conversations_user
    ON ai.conversations(user_id, last_message_at DESC);

CREATE TABLE IF NOT EXISTS ai.messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID         NOT NULL REFERENCES ai.conversations(id) ON DELETE CASCADE,
    tenant_id       UUID         NOT NULL,
    role            VARCHAR(20)  NOT NULL, -- user | assistant | system
    content         TEXT         NOT NULL,
    token_count     INTEGER,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai.embeddings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    source_type     VARCHAR(50)  NOT NULL, -- interaction | document | note
    source_id       UUID         NOT NULL,
    embedding       vector(1536) NOT NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- HNSW index for fast approximate nearest-neighbour cosine search
CREATE INDEX IF NOT EXISTS ix_embeddings_hnsw
    ON ai.embeddings
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- ============================================================
-- SECURITY SCHEMA — audit logs
-- ============================================================

CREATE TABLE IF NOT EXISTS security.audit_logs (
    id              UUID NOT NULL DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    user_id         UUID,
    action          VARCHAR(100) NOT NULL,
    resource        VARCHAR(100),
    resource_id     UUID,
    ip_address      INET,
    user_agent      TEXT,
    metadata        JSONB        DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)             -- must include partition key
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS security.audit_logs_2026_07
    PARTITION OF security.audit_logs
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');

CREATE INDEX IF NOT EXISTS ix_audit_tenant_created
    ON security.audit_logs(tenant_id, created_at DESC);

-- ============================================================
-- ROW-LEVEL SECURITY
-- ============================================================

-- Enable RLS on all multi-tenant tables
ALTER TABLE customers.customers          ENABLE ROW LEVEL SECURITY;
ALTER TABLE customers.customer_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions.churn_predictions   ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions.lead_scores         ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions.health_scores       ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations.crm_connections    ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations.sync_jobs          ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.conversations                ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.messages                     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.embeddings                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE security.audit_logs             ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- PHASE 3 — Enterprise AI Intelligence Platform
-- ============================================================

-- ============================================================
-- AI SCHEMA — Phase 3: Agents
-- ============================================================

CREATE TABLE IF NOT EXISTS ai.agents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    name            VARCHAR(100) NOT NULL,
    agent_type      VARCHAR(50)  NOT NULL, -- sales|marketing|customer_success|executive|workflow|recommendation|analytics
    identity        TEXT         NOT NULL,
    goal            TEXT         NOT NULL,
    system_prompt   TEXT         NOT NULL,
    tools           JSONB        NOT NULL DEFAULT '[]',
    permissions     JSONB        NOT NULL DEFAULT '{}',
    config          JSONB        NOT NULL DEFAULT '{}',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_agents_tenant_type ON ai.agents(tenant_id, agent_type);

CREATE TABLE IF NOT EXISTS ai.agent_memory (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    agent_id        UUID         NOT NULL REFERENCES ai.agents(id) ON DELETE CASCADE,
    memory_type     VARCHAR(50)  NOT NULL, -- session|customer|meeting|business|agent
    content         JSONB        NOT NULL DEFAULT '{}',
    embedding       vector(1536),
    importance_score FLOAT       DEFAULT 0.0,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_agent_memory_agent_type ON ai.agent_memory(agent_id, memory_type);
CREATE INDEX IF NOT EXISTS ix_agent_memory_embedding ON ai.agent_memory USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE TABLE IF NOT EXISTS ai.agent_conversations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    session_id      UUID         NOT NULL,
    from_agent      UUID         NOT NULL REFERENCES ai.agents(id),
    to_agent        UUID         NOT NULL REFERENCES ai.agents(id),
    message_type    VARCHAR(50)  NOT NULL, -- query|response|broadcast|delegate
    content         JSONB        NOT NULL DEFAULT '{}',
    status          VARCHAR(50)  NOT NULL DEFAULT 'pending',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_agent_conversations_session ON ai.agent_conversations(session_id, created_at);

-- ============================================================
-- AI SCHEMA — Phase 3: Knowledge Graph
-- ============================================================

CREATE TABLE IF NOT EXISTS ai.knowledge_nodes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    node_type       VARCHAR(50)  NOT NULL, -- Customer|Organization|Lead|Deal|Meeting|Employee|Activity|Email|Recommendation|Workflow
    external_id     VARCHAR(255),
    name            VARCHAR(255) NOT NULL,
    labels          TEXT[]       NOT NULL DEFAULT '{}',
    properties      JSONB        NOT NULL DEFAULT '{}',
    embedding       vector(1536),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_knowledge_nodes_type ON ai.knowledge_nodes(node_type, tenant_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_nodes_embedding ON ai.knowledge_nodes USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE TABLE IF NOT EXISTS ai.knowledge_edges (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    source_node_id  UUID         NOT NULL REFERENCES ai.knowledge_nodes(id) ON DELETE CASCADE,
    target_node_id  UUID         NOT NULL REFERENCES ai.knowledge_nodes(id) ON DELETE CASCADE,
    edge_type       VARCHAR(100) NOT NULL, -- HAS_DEAL|HAS_MEETING|HAS_ACTIVITY|SENT_EMAIL|HAS_RECOMMENDATION|BELONGS_TO|PARTICIPATED_IN|LED_TO|HAS_OUTCOME
    properties      JSONB        NOT NULL DEFAULT '{}',
    weight          FLOAT        DEFAULT 1.0,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_knowledge_edges_source ON ai.knowledge_edges(source_node_id);
CREATE INDEX IF NOT EXISTS ix_knowledge_edges_target ON ai.knowledge_edges(target_node_id);

-- ============================================================
-- AI SCHEMA — Phase 3: Customer Digital Twins
-- ============================================================

CREATE TABLE IF NOT EXISTS ai.customer_twins (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    customer_id     UUID         NOT NULL REFERENCES customers.customers(id) ON DELETE CASCADE,
    buying_behaviour JSONB       NOT NULL DEFAULT '{}',
    price_sensitivity FLOAT      DEFAULT 0.0,
    renewal_probability FLOAT    DEFAULT 0.0,
    risk_level      VARCHAR(20)  NOT NULL DEFAULT 'low',
    preferred_channel VARCHAR(50) DEFAULT 'email',
    communication_frequency VARCHAR(20) DEFAULT 'weekly',
    product_affinity JSONB       NOT NULL DEFAULT '[]',
    lifetime_value  FLOAT        DEFAULT 0.0,
    attributes      JSONB        NOT NULL DEFAULT '{}',
    last_updated_at TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS ix_customer_twins_customer ON ai.customer_twins(tenant_id, customer_id);

-- ============================================================
-- AI SCHEMA — Phase 3: Reasoning & Simulation
-- ============================================================

CREATE TABLE IF NOT EXISTS ai.reasoning_pipelines (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    query           TEXT         NOT NULL,
    pipeline_steps  JSONB        NOT NULL DEFAULT '[]',
    evidence        JSONB        NOT NULL DEFAULT '{}',
    confidence      FLOAT        NOT NULL DEFAULT 0.0,
    business_impact JSONB        NOT NULL DEFAULT '{}',
    recommendations JSONB        NOT NULL DEFAULT '[]',
    status          VARCHAR(50)  NOT NULL DEFAULT 'completed',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_reasoning_pipelines_tenant ON ai.reasoning_pipelines(tenant_id, created_at DESC);

CREATE TABLE IF NOT EXISTS ai.simulation_runs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    name            VARCHAR(255) NOT NULL,
    simulation_type VARCHAR(50)  NOT NULL, -- pricing|marketing|renewals|upsell|retention|discount
    parameters      JSONB        NOT NULL DEFAULT '{}',
    scenarios       JSONB        NOT NULL DEFAULT '[]',
    results         JSONB        NOT NULL DEFAULT '{}',
    status          VARCHAR(50)  NOT NULL DEFAULT 'running',
    started_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS ix_simulation_runs_tenant ON ai.simulation_runs(tenant_id, created_at DESC);

CREATE TABLE IF NOT EXISTS ai.simulation_results (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    run_id          UUID         NOT NULL REFERENCES ai.simulation_runs(id) ON DELETE CASCADE,
    scenario_name   VARCHAR(255) NOT NULL,
    projected_revenue FLOAT      DEFAULT 0.0,
    projected_profit FLOAT       DEFAULT 0.0,
    projected_retention FLOAT    DEFAULT 0.0,
    expected_churn  FLOAT        DEFAULT 0.0,
    confidence      FLOAT        DEFAULT 0.0,
    details         JSONB        NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_simulation_results_run ON ai.simulation_results(run_id);

-- ============================================================
-- AI SCHEMA — Phase 3: Semantic Search
-- ============================================================

CREATE TABLE IF NOT EXISTS ai.semantic_documents (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    source_type     VARCHAR(50)  NOT NULL, -- customer|meeting|email|activity|recommendation|ticket
    source_id       VARCHAR(255) NOT NULL,
    title           VARCHAR(500),
    content         TEXT         NOT NULL,
    embedding       vector(1536) NOT NULL,
    metadata        JSONB        NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_semantic_documents_embedding ON ai.semantic_documents USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS ix_semantic_documents_source ON ai.semantic_documents(source_type, source_id);

-- ============================================================
-- OBSERVABILITY SCHEMA — Phase 3
-- ============================================================

CREATE TABLE IF NOT EXISTS ai.agent_logs (
    id              UUID NOT NULL DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    agent_id        UUID         NOT NULL REFERENCES ai.agents(id),
    action          VARCHAR(100) NOT NULL,
    prompt_tokens   INTEGER      DEFAULT 0,
    completion_tokens INTEGER    DEFAULT 0,
    latency_ms      INTEGER      DEFAULT 0,
    llm_cost        FLOAT        DEFAULT 0.0,
    status          VARCHAR(50)  NOT NULL DEFAULT 'success',
    error_message   TEXT,
    metadata        JSONB        NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS ai.agent_logs_2026_07
    PARTITION OF ai.agent_logs
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');

CREATE TABLE IF NOT EXISTS ai.agent_logs_2026_08
    PARTITION OF ai.agent_logs
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

CREATE INDEX IF NOT EXISTS ix_agent_logs_agent ON ai.agent_logs(agent_id, created_at DESC);

-- ============================================================
-- TRIGGER: Auto-update customer_twins on CRM events
-- ============================================================

CREATE OR REPLACE FUNCTION ai.trigger_twin_update()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE ai.customer_twins
    SET last_updated_at = NOW()
    WHERE customer_id = NEW.customer_id AND tenant_id = NEW.tenant_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- RLS POLICIES FOR PHASE 3 TABLES
-- ============================================================

ALTER TABLE ai.agents              ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.agent_memory        ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.agent_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.knowledge_nodes     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.knowledge_edges     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.customer_twins      ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.reasoning_pipelines ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.simulation_runs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.simulation_results  ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.semantic_documents  ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.agent_logs          ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON ai.agents
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.agent_memory
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.agent_conversations
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.knowledge_nodes
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.knowledge_edges
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.customer_twins
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.reasoning_pipelines
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.simulation_runs
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.simulation_results
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.semantic_documents
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.agent_logs
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- ============================================================
-- Phase 2 Tables (existing)
-- ============================================================

CREATE TABLE IF NOT EXISTS workflows.workflows (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    name            VARCHAR(255) NOT NULL,
    description     VARCHAR(1000),
    conditions      JSONB        NOT NULL DEFAULT '{}',
    actions         JSONB        NOT NULL DEFAULT '[]',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_workflows_tenant_status ON workflows.workflows(tenant_id, is_active);

CREATE TABLE IF NOT EXISTS ai.recommendations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    customer_id     UUID         NOT NULL REFERENCES customers.customers(id) ON DELETE CASCADE,
    type            VARCHAR(100) NOT NULL,
    confidence      FLOAT        NOT NULL,
    expected_revenue FLOAT       NOT NULL DEFAULT 0.0,
    status          VARCHAR(50)  NOT NULL DEFAULT 'Pending',
    business_reason TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_recommendations_tenant_customer ON ai.recommendations(tenant_id, customer_id);

CREATE TABLE IF NOT EXISTS ai.feedback_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    recommendation_id UUID       NOT NULL,
    user_id         UUID         NOT NULL REFERENCES core.users(id) ON DELETE CASCADE,
    feedback_text   TEXT,
    rating          INTEGER,
    outcome_achieved BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_feedback_tenant_recommendation ON ai.feedback_logs(tenant_id, recommendation_id);

CREATE TABLE IF NOT EXISTS ai.meeting_summaries (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID         NOT NULL,
    customer_id     UUID         NOT NULL REFERENCES customers.customers(id) ON DELETE CASCADE,
    transcript_summary TEXT,
    action_items    JSONB        NOT NULL DEFAULT '[]',
    sentiment       VARCHAR(50),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_meetings_tenant_customer ON ai.meeting_summaries(tenant_id, customer_id);

ALTER TABLE workflows.workflows      ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.recommendations       ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.feedback_logs         ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai.meeting_summaries     ENABLE ROW LEVEL SECURITY;

-- Tenant isolation policy (app sets app.tenant_id at session start)
CREATE POLICY tenant_isolation ON customers.customers
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON predictions.churn_predictions
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON predictions.lead_scores
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON predictions.health_scores
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON integrations.crm_connections
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.conversations
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.embeddings
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON security.audit_logs
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON workflows.workflows
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.recommendations
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.feedback_logs
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

CREATE POLICY tenant_isolation ON ai.meeting_summaries
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- ============================================================
-- VECTOR SIMILARITY SEARCH FUNCTION
-- ============================================================

CREATE OR REPLACE FUNCTION ai.find_similar(
    query_embedding vector(1536),
    p_tenant_id     UUID,
    p_source_type   TEXT DEFAULT NULL,
    p_limit         INT  DEFAULT 10
)
RETURNS TABLE (
    source_id   UUID,
    source_type TEXT,
    similarity  FLOAT
)
LANGUAGE sql STABLE AS $$
    SELECT
        source_id,
        source_type,
        1 - (embedding <=> query_embedding) AS similarity
    FROM ai.embeddings
    WHERE tenant_id = p_tenant_id
      AND (p_source_type IS NULL OR source_type = p_source_type)
    ORDER BY embedding <=> query_embedding
    LIMIT p_limit;
$$;

-- ============================================================
-- SEED: default super-admin tenant (dev only — remove in prod)
-- ============================================================
INSERT INTO core.tenants (id, name, slug, plan)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Miracle Birds Dev',
    'dev',
    'enterprise'
) ON CONFLICT (slug) DO NOTHING;

-- ============================================================
-- PHASE 4 — Autonomous Enterprise AI Platform Services
-- ============================================================

-- Reinforcement Learning
CREATE TABLE IF NOT EXISTS ai.rl_episodes (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL,
    state           JSONB NOT NULL DEFAULT '{}',
    action          VARCHAR(255) NOT NULL,
    reward          FLOAT NOT NULL DEFAULT 0.0,
    outcome         VARCHAR(255) NOT NULL,
    policy_version  VARCHAR(100) DEFAULT 'v1',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_rl_episodes_tenant ON ai.rl_episodes(tenant_id, created_at DESC);
ALTER TABLE ai.rl_episodes ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON ai.rl_episodes
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- Marketplace Plugins
CREATE TABLE IF NOT EXISTS core.marketplace_items (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) UNIQUE NOT NULL,
    item_type       VARCHAR(50) NOT NULL, -- agent | crm | automation | analytics
    description     TEXT,
    developer       VARCHAR(255) DEFAULT 'Miracle Birds',
    price           FLOAT DEFAULT 0.0,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS core.installed_plugins (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    plugin_id       UUID NOT NULL REFERENCES core.marketplace_items(id) ON DELETE CASCADE,
    settings        JSONB DEFAULT '{}',
    installed_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, plugin_id)
);
ALTER TABLE core.installed_plugins ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON core.installed_plugins
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- Public API Keys
CREATE TABLE IF NOT EXISTS core.api_keys (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,
    name            VARCHAR(255) NOT NULL,
    key_hash        TEXT UNIQUE NOT NULL,
    scopes          TEXT[] NOT NULL DEFAULT '{}',
    expires_at      TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE core.api_keys ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON core.api_keys
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- Workflow Executions
CREATE TABLE IF NOT EXISTS workflows.executions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL,
    workflow_id     UUID REFERENCES workflows.workflows(id) ON DELETE SET NULL,
    workflow_name   VARCHAR(255) NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'running', -- running | completed | failed | rolled_back
    actions_run     JSONB NOT NULL DEFAULT '[]',
    context_data    JSONB NOT NULL DEFAULT '{}',
    retries         INTEGER DEFAULT 0,
    error_message   TEXT,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
ALTER TABLE workflows.executions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON workflows.executions
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- GDPR Consent Logs
CREATE TABLE IF NOT EXISTS security.consent_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL,
    customer_id     UUID NOT NULL REFERENCES customers.customers(id) ON DELETE CASCADE,
    consent_type    VARCHAR(100) NOT NULL, -- email_marketing | data_processing | profiling
    granted         BOOLEAN NOT NULL,
    ip_address      INET,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE security.consent_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON security.consent_logs
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- Threat Alerts
CREATE TABLE IF NOT EXISTS security.threat_alerts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       UUID NOT NULL,
    threat_type     VARCHAR(100) NOT NULL, -- brute_force | sql_injection | prompt_injection | bulk_export
    severity        VARCHAR(20) NOT NULL, -- low | medium | high | critical
    description     TEXT NOT NULL,
    ip_address      INET,
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE security.threat_alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON security.threat_alerts
    USING (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- Seed marketplace items
INSERT INTO core.marketplace_items (name, slug, item_type, description, developer, price)
VALUES 
    ('Salesforce Sync Connector', 'salesforce-sync', 'crm', 'Bi-directional sync with Salesforce CRM records, support for real-time contact and deal updates.', 'Miracle Birds', 0.0),
    ('HubSpot Connector Pro', 'hubspot-pro', 'crm', 'Advanced analytics integration and real-time timeline syncing for HubSpot accounts.', 'HubSpot Inc', 49.0),
    ('Security Agent Shield', 'security-agent', 'agent', 'Upgraded Security Agent with Zero-Trust firewall rules, compliance logs scanning and audit reports.', 'Miracle Birds Security', 199.0),
    ('Slack Notify Automation', 'slack-notify', 'automation', 'Instantly trigger workflows to notify slack channels when customer health scores drops.', 'Miracle Birds', 0.0),
    ('Deep Sentiment Extension', 'deep-sentiment', 'analytics', 'Uses custom NLP models to extract granular customer sentiment scores from emails.', 'Sentiment Labs', 29.0)
ON CONFLICT (slug) DO NOTHING;

