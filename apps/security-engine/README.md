# 🔒 Security Engine — Miracle Birds

Enterprise security layer: prompt injection firewall, PII detection, audit logging.

## Technology Stack

- **FastAPI** — REST API (port 8004)
- **Microsoft Presidio** — PII detection & anonymization
- **spaCy** — NER for name/address detection
- **Regex patterns** — Fast PII pattern matching
- **Custom ML** — Injection classifier (optional)

## Core Modules

### Prompt Injection Firewall

Two-stage detection pipeline:

1. **Pattern matching** (< 5ms) — 10+ regex patterns for common attacks
2. **ML classifier** (< 100ms) — Catches subtle/novel injections

### PII Detection & Masking

Supported PII types: email, phone, SSN, credit card, IP address, names (NER), addresses (NER)

Masking strategies: partial masking, full redaction, tokenization

## API Endpoints

```
POST /firewall/scan   — Scan text for prompt injection
POST /pii/detect      — Detect PII entities
POST /pii/mask        — Mask all PII in text
POST /audit/log       — Record audit event
GET  /audit/logs/{id} — Retrieve audit logs
GET  /health          — Health check
```

## Development

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --reload --port 8004
```
