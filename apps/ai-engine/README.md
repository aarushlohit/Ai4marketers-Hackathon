# 🤖 AI Engine — Miracle Birds

LLM orchestration service powering the AI Copilot, RAG pipeline, and agent workflows.

## Technology Stack

- **FastAPI** — REST API (port 8001)
- **LangChain 0.1 + LangGraph** — Agent orchestration
- **OpenAI GPT-4-turbo** — Primary LLM
- **Google Gemini Pro** — Secondary LLM (fallback)
- **text-embedding-ada-002** — Vector embeddings
- **pgvector** — Vector similarity search
- **Redis** — Conversation memory

## Key Modules

| Module                      | Description                                    |
| --------------------------- | ---------------------------------------------- |
| `app/agents/crm_copilot.py` | CRM Copilot agent with RAG + security          |
| `app/core/llm.py`           | Model-agnostic LLM factory (OpenAI / Gemini)   |
| `app/api/chat.py`           | Chat endpoints with Redis conversation history |
| `app/api/embeddings.py`     | Embedding generation endpoints                 |

## API Endpoints

```
POST /chat          — Send message to Copilot
POST /embeddings    — Generate vector embeddings
GET  /health        — Health check
```

## Security Integration

Every user message is scanned by the Security Engine's prompt injection firewall before being sent to the LLM. Every LLM response is scanned for PII before being returned to the user.

## Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```
