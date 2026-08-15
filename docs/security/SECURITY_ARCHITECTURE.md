# 🔒 Security Architecture

## Miracle Birds — Enterprise Security Design

**Version:** 1.0 | **Date:** July 13, 2026 | **Classification:** Confidential

---

## Defense in Depth — 7 Security Layers

```
Layer 1: Network Security
  └─ VPC isolation, Security Groups, AWS WAF, DDoS (Shield Standard)

Layer 2: Perimeter Security
  └─ API Gateway, Rate Limiting, IP allowlisting, Bot protection

Layer 3: Application Security
  └─ Input validation, OWASP Top 10, CSP headers, CORS policy

Layer 4: AI-Specific Security
  └─ Prompt injection firewall, PII scrubbing, content filtering

Layer 5: Authentication & Authorization
  └─ JWT + RBAC + MFA, session management, OAuth 2.0

Layer 6: Data Security
  └─ AES-256 at rest, TLS 1.3 in transit, column-level encryption

Layer 7: Security Monitoring
  └─ SIEM, anomaly detection, audit logging, incident response
```

---

## AI Security Components

### Prompt Injection Firewall

All user inputs to the AI system pass through a two-stage firewall before reaching the LLM:

**Stage 1 — Pattern Matching (< 5ms):**

```python
INJECTION_PATTERNS = [
    r"ignore\s+previous\s+instructions",
    r"you\s+are\s+now\s+a\s+different",
    r"forget\s+your\s+system\s+prompt",
    r"act\s+as\s+if\s+you\s+are",
    r"jailbreak|DAN\s+mode|developer\s+mode",
    r"print\s+your\s+system\s+prompt",
    r"reveal\s+your\s+instructions",
]
```

**Stage 2 — ML Classifier (~50ms):**

- Fine-tuned DistilBERT on injection dataset
- Threshold: 0.85 confidence → block
- Target: < 5% false positive rate

### PII Detection & Masking

Supported PII types and masking strategies:

| PII Type    | Detection Method | Masking               |
| ----------- | ---------------- | --------------------- |
| Email       | Regex            | `j***@example.com`    |
| Phone       | Regex            | `***-***-1234`        |
| SSN         | Regex            | `***-**-1234`         |
| Credit Card | Regex + Luhn     | `****-****-****-1234` |
| Name        | NER (spaCy)      | `[NAME]`              |
| Address     | NER              | `[ADDRESS]`           |
| IP Address  | Regex            | `***.***.***.123`     |

### Content Filtering

Blocks output that contains:

- Competitor intelligence leakage
- Cross-tenant data bleed
- Harmful or policy-violating content

---

## Authentication & Authorization

### JWT Token Design

```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "role": "admin",
  "permissions": ["customers:read", "customers:write", "predictions:read"],
  "iat": 1689282000,
  "exp": 1689283800
}
```

- Access token TTL: **30 minutes** (signed HS256)
- Refresh token TTL: **7 days** (rotated on each refresh)
- Refresh tokens stored in Redis (revocable)

### RBAC Role Matrix

| Permission          | Super Admin | Admin | Manager | User | Viewer |
| ------------------- | :---------: | :---: | :-----: | :--: | :----: |
| Manage tenants      |     ✅      |  ❌   |   ❌    |  ❌  |   ❌   |
| Manage users        |     ✅      |  ✅   |   ❌    |  ❌  |   ❌   |
| View all data       |     ✅      |  ✅   |   ✅    |  ✅  |   ✅   |
| Edit customers      |     ✅      |  ✅   |   ✅    |  ✅  |   ❌   |
| Run predictions     |     ✅      |  ✅   |   ✅    |  ✅  |   ❌   |
| Manage workflows    |     ✅      |  ✅   |   ✅    |  ❌  |   ❌   |
| Manage integrations |     ✅      |  ✅   |   ❌    |  ❌  |   ❌   |
| Delete data         |     ✅      |  ✅   |   ❌    |  ❌  |   ❌   |

### Multi-Factor Authentication

Supported MFA methods:

- **TOTP** (Google Authenticator, Authy) — Primary
- **SMS OTP** — Secondary
- **Email OTP** — Fallback

---

## Data Protection

### Encryption at Rest

| Data Store | Method              | Key Management      |
| ---------- | ------------------- | ------------------- |
| PostgreSQL | TDE (pg_tde)        | AWS KMS             |
| Redis      | Encryption at rest  | ElastiCache default |
| S3         | AES-256-SSE         | AWS KMS CMK         |
| Secrets    | AWS Secrets Manager | AWS KMS             |

### Encryption in Transit

- All external traffic: **TLS 1.3** minimum
- Internal microservice traffic: **mTLS** (mutual TLS)
- Certificate management: **AWS ACM** + cert-manager (Kubernetes)

---

## Compliance Framework

| Standard       | Requirement                | Implementation              |
| -------------- | -------------------------- | --------------------------- |
| GDPR Art. 17   | Right to erasure (30 days) | Anonymization API           |
| GDPR Art. 15   | Right to access            | Data export endpoint        |
| GDPR Art. 20   | Right to portability       | JSON/CSV export             |
| GDPR Art. 33   | Breach notification 72h    | Incident response plan      |
| SOC 2 CC6      | Logical access controls    | RBAC + MFA                  |
| SOC 2 CC7      | System monitoring          | Prometheus + Grafana + SIEM |
| HIPAA §164.312 | Access controls + audit    | RBAC + immutable audit log  |
| CCPA §1798.105 | Right to delete            | Same as GDPR erasure        |

---

## Incident Response

### Severity Levels

| Level         | Description                   | Response SLA | Examples                            |
| ------------- | ----------------------------- | ------------ | ----------------------------------- |
| P0 — Critical | Active breach / data exposure | 15 min       | DB compromise, mass data exfil      |
| P1 — High     | Security control failure      | 1 hour       | Auth bypass, injection success      |
| P2 — Medium   | Suspicious activity           | 4 hours      | Brute force, unusual access pattern |
| P3 — Low      | Policy violation              | 24 hours     | Rate limit exceeded, weak password  |

### Response Phases

```
1. Detection    → SIEM alert / automated detection
2. Triage       → Assess severity, assign owner (15 min)
3. Containment  → Isolate affected systems (P0: immediate)
4. Eradication  → Remove threat, patch vulnerability
5. Recovery     → Restore service, verify integrity
6. Post-Incident → Blameless review, update runbooks
```

---

## Security Monitoring KPIs

| Metric                               | Target             |
| ------------------------------------ | ------------------ |
| Mean Time to Detect (MTTD)           | < 15 minutes       |
| Mean Time to Respond (MTTR)          | < 1 hour           |
| False Positive Rate                  | < 5%               |
| Vulnerability Remediation (Critical) | < 24 hours         |
| Security Scan Frequency              | Weekly (automated) |

---

**Version:** 1.0 | **Last Updated:** July 13, 2026
