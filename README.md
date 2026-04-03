# Conversational CV Builder — POC

> **Stack:** Angular SPA · Python FastAPI · OpenAI GPT-4.1 · Whisper · Okta

A guided, conversational CV-building application. Users interact via chat or voice,
upload an existing CV for AI extraction, and export polished documents in PDF, DOCX, or JSON.

---

## Repository Layout

```
cv-builder/
├── backend/          # Python FastAPI application
├── frontend/         # Angular 17 SPA
├── docker-compose.yml
└── README.md
```

---

## Quick Start

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 20 LTS |
| Angular CLI | 17+ |
| Docker / Docker Compose | 24+ |

---

### 1 — Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt

# Copy and fill in secrets
copy .env.example .env

uvicorn app.main:app --reload --port 8000
```

API docs → http://localhost:8000/docs

Development auth note: when `APP_ENV=development`, backend auth is bypassed for local testing.

---

### 2 — Frontend

```bash
cd frontend
npm install
ng serve
```

App → http://localhost:4200

---

### 3 — Docker Compose (both services)

```bash
docker-compose up --build
```

---

## POC LLM Integration Test

Run a quick end-to-end test of the GPT-4.1 integration without starting the full server:

```bash
cd backend
python tests/test_llm_integration.py
```

Requires `OPENAI_API_KEY` to be set in `backend/.env`.

Or validate via API after starting backend:

```bash
curl -X POST http://localhost:8000/api/llm/test \
	-H "Content-Type: application/json" \
	-d '{"prompt":"Give me two concise CV bullets for a FastAPI engineer."}'
```

---

## Environment Variables

See `backend/.env.example` for the full list.

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_MODEL` | Model name (default: `gpt-4.1`) |
| `OKTA_DOMAIN` | Okta tenant domain |
| `OKTA_CLIENT_ID` | Okta client ID |
| `APP_ENV` | `development` / `production` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins |

---

## Design Reference

See the `/docs` folder or the companion LLD document for sequence diagrams and API contract.
