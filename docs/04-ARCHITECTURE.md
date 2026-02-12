# 4. Architektur & Tech-Stack
## Systemübersicht
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  FRONTEND                                    │
│                         React + TypeScript + Tailwind                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Login Page  │  │ Use Case    │  │ Use Case    │  │ Chat Panel          │ │
│  │             │  │ List        │  │ Detail/Edit │  │ (Agent Interface)   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                      │                         │             │
└──────────────────────────────────────┼─────────────────────────┼─────────────┘
                                       │ HTTP/REST               │ HTTP/REST
                                       ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  BACKEND                                     │
│                            FastAPI + SQLAlchemy                              │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                            API Layer (Routers)                          ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      ││
│  │  │ /auth    │ │/use-cases│ │/companies│ │/transcr. │ │ /chat    │      ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│  ┌───────────────────────────────────┼───────────────────────────────────┐  │
│  │                           Service Layer                               │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │  │
│  │  │ UseCaseService  │  │ TranscriptSvc   │  │ AgentService    │       │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                       │
│  ┌───────────────────────────────────┼───────────────────────────────────┐  │
│  │                           Agent Layer                                 │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │  │
│  │  │ Tool Registry   │  │ Tool Executor   │  │ LLM Client      │       │  │
│  │  │ (7+ Tools)      │  │ (Calling Loop)  │  │ (OpenRouter)    │       │  │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                       │
│  ┌───────────────────────────────────┼───────────────────────────────────┐  │
│  │                           Data Layer                                  │  │
│  │  ┌─────────────────┐  ┌─────────────────┐                            │  │
│  │  │ SQLAlchemy ORM  │  │ Pydantic Schemas│                            │  │
│  │  │ (Models)        │  │ (Validation)    │                            │  │
│  │  └─────────────────┘  └─────────────────┘                            │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────┼───────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                 DATABASE                                     │
│                                  SQLite                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Industry │ │ Company  │ │ User     │ │Transcript│ │ UseCase  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ HTTPS
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL SERVICES                               │
│                                OpenRouter API                                │
│                          (LLM: Claude 3 Haiku)                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech-Stack
### Backend
| Komponente | Technologie | Version | Begründung |
|------------|-------------|---------|------------|
| Runtime | Python | 3.11+ | Stabil, gutes LLM-Ecosystem |
| Web Framework | FastAPI | 0.109+ | Schnell, typisiert, automatische OpenAPI-Docs |
| ORM | SQLAlchemy | 2.0+ | Industriestandard, sauber abstrahiert |
| Validation | Pydantic | 2.0+ | Integriert mit FastAPI, strict typing |
| Database | SQLite | 3 | Zero-Config, ausreichend für Prototyp |
| Auth | python-jose, passlib | - | JWT-Handling, Password-Hashing (bcrypt) |
| HTTP Client | httpx | - | Async-Support für OpenRouter-Calls |
| Testing | pytest | - | Standard für Python |

### Frontend
| Komponente | Technologie | Version | Begründung |
|------------|-------------|---------|------------|
| Framework | React | 18+ | Industriestandard, große Community |
| Language | TypeScript | 5+ | Type-Safety, bessere DX |
| Build Tool | Vite | 5+ | Schnell, modernes Tooling |
| Styling | Tailwind CSS | 3+ | Utility-first, schnelles Prototyping |
| HTTP Client | fetch (native) | - | Keine zusätzliche Dependency |
| State | React Context | - | Ausreichend für MVP, kein Redux-Overhead |

### Infrastructure
| Komponente | Technologie | Begründung |
|------------|-------------|------------|
| Containerization | Docker + docker-compose | Einfaches lokales Setup |
| LLM Provider | OpenRouter | Zugang zu verschiedenen Modellen |
| LLM Model | Claude 3 Haiku | Günstig, schnell, gut für Extraktion |

---
## Datenmodell
### Entity-Relationship-Diagramm

```
┌─────────────────┐
│    Industry     │
├─────────────────┤
│ id (PK)         │
│ name            │
│ description     │
│ created_at      │
└────────┬────────┘
         │ 1
         │
         │ n
┌────────▼────────┐       ┌─────────────────┐
│    Company      │       │      User       │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ name            │       │ email (unique)  │
│ industry_id(FK) │       │ password_hash   │
│ created_at      │       │ role (enum)     │
└────────┬────────┘       │ created_at      │
         │ 1              └────────┬────────┘
         │                         │
         │ n                       │ 1 (created_by)
┌────────▼────────┐                │
│   Transcript    │                │
├─────────────────┤                │
│ id (PK)         │                │
│ filename        │                │
│ content (text)  │                │
│ company_id (FK) │                │
│ uploaded_by(FK) │◄───────────────┘
│ created_at      │
└────────┬────────┘
         │ 1 (optional)
         │
         │ n
┌────────▼─────────────────────────┐
│            UseCase               │
├──────────────────────────────────┤
│ id (PK)                          │
│ title                            │
│ description                      │
│ stakeholders (JSON)              │
│ expected_benefit                 │
│ status (enum)                    │
│ company_id (FK)                  │
│ transcript_id (FK, nullable)     │
│ created_by (FK)                  │
│ created_at                       │
│ updated_at                       │
└──────────────────────────────────┘
```

### Enums
```python
class Role(str, Enum):
    READER = "reader"
    MAINTAINER = "maintainer"
    ADMIN = "admin"

class UseCaseStatus(str, Enum):
    NEW = "new"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"
```

### Stakeholder-Struktur (JSON)
```json
{
  "stakeholders": [
    {
      "name": "Max Müller",
      "role": "Vertriebsleiter"
    },
    {
      "name": "Anna Schmidt",
      "role": "IT-Leiterin"
    }
  ]
}
```

---

## API-Design
### Endpoints
| Method | Endpoint | Beschreibung | Auth | RBAC |
|--------|----------|--------------|------|------|
| POST | /auth/register | User registrieren | - | - |
| POST | /auth/login | Login, JWT erhalten | - | - |
| GET | /auth/me | Aktueller User | ✅ | Reader+ |
| GET | /industries | Branchen auflisten | ✅ | Reader+ |
| GET | /companies | Unternehmen auflisten | ✅ | Reader+ |
| POST | /companies | Unternehmen anlegen | ✅ | Maintainer+ |
| GET | /transcripts | Transkripte auflisten | ✅ | Reader+ |
| POST | /transcripts | Transkript hochladen + extrahieren | ✅ | Maintainer+ |
| GET | /use-cases | Use Cases auflisten (mit Filtern) | ✅ | Reader+ |
| GET | /use-cases/{id} | Use Case Detail | ✅ | Reader+ |
| POST | /use-cases | Use Case anlegen | ✅ | Maintainer+ |
| PATCH | /use-cases/{id} | Use Case bearbeiten | ✅ | Maintainer+ |
| DELETE | /use-cases/{id} | Use Case archivieren | ✅ | Admin |
| POST | /chat | Agent-Interaktion | ✅ | Reader+ (RBAC pro Tool) |

### Response-Format
```json
{
  "data": { ... },
  "meta": {
    "total": 42,
    "page": 1,
    "per_page": 20
  }
}
```

### Error-Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "title",
        "message": "Field is required"
      }
    ]
  }
}
```

---

## Agent-Architektur
### Tool-Calling-Flow
```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │────▶│  /chat   │────▶│  Agent   │────▶│OpenRouter│
│  Input   │     │ Endpoint │     │  Loop    │     │   LLM    │
└──────────┘     └──────────┘     └────┬─────┘     └────┬─────┘
                                       │                │
                                       │◄───────────────┘
                                       │   Tool Call?
                                       ▼
                                 ┌──────────┐
                           No ◄──┤ Decision ├──▶ Yes
                                 └──────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      ▼                                  ▼
               ┌──────────┐                       ┌──────────┐
               │ Return   │                       │ Execute  │
               │ Response │                       │ Tool     │
               └──────────┘                       └────┬─────┘
                                                       │
                                                       ▼
                                                 ┌──────────┐
                                                 │ RBAC     │
                                                 │ Check    │
                                                 └────┬─────┘
                                                       │
                                         ┌─────────────┴─────────────┐
                                         ▼                           ▼
                                   ┌──────────┐                ┌──────────┐
                                   │ Allowed  │                │ Denied   │
                                   │ Execute  │                │ Error    │
                                   └────┬─────┘                └──────────┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │ Tool     │
                                  │ Result   │
                                  └────┬─────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │ Loop: Send     │
                              │ Result to LLM  │
                              └────────────────┘
```

### Tools
| Tool | Input | Output | RBAC |
|------|-------|--------|------|
| list_use_cases | `{filters?: {company_id?, status?, search?}}` | `UseCase[]` | Reader+ |
| get_use_case | `{id: int}` | `UseCase` | Reader+ |
| create_use_case | `{title, description, company_id, ...}` | `UseCase` | Maintainer+ |
| update_use_case | `{id, fields: {...}}` | `UseCase` | Maintainer+ |
| set_status | `{id, status}` | `UseCase` | Maintainer+ |
| archive_use_case | `{id}` | `{success: bool}` | Admin |
| analyze_transcript | `{transcript_id}` | `UseCase[]` | Maintainer+ |
| list_companies | `{}` | `Company[]` | Reader+ |

---

## Projektstruktur
```
use-case-manager/
├── README.md
├── DECISIONS.md
├── CHANGELOG.md
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── docs/
│   ├── 01-SCOPE.md
│   ├── 02-RISKS.md
│   ├── 03-DATA.md
│   ├── 04-ARCHITECTURE.md
│   └── 05-BACKLOG.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                    # DB Migrations (optional)
│   │   └── ...
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI App
│   │   ├── config.py               # Settings
│   │   ├── database.py             # DB Connection
│   │   ├── dependencies.py         # DI (Auth, DB Session)
│   │   │
│   │   ├── models/                 # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── industry.py
│   │   │   ├── company.py
│   │   │   ├── user.py
│   │   │   ├── transcript.py
│   │   │   └── use_case.py
│   │   │
│   │   ├── schemas/                # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── industry.py
│   │   │   ├── company.py
│   │   │   ├── transcript.py
│   │   │   └── use_case.py
│   │   │
│   │   ├── routers/                # API Endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── industries.py
│   │   │   ├── companies.py
│   │   │   ├── transcripts.py
│   │   │   ├── use_cases.py
│   │   │   └── chat.py
│   │   │
│   │   ├── services/               # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── use_case_service.py
│   │   │   └── transcript_service.py
│   │   │
│   │   ├── agent/                  # Agent Implementation
│   │   │   ├── __init__.py
│   │   │   ├── agent.py            # Main Agent Loop
│   │   │   ├── tools.py            # Tool Definitions
│   │   │   └── executor.py         # Tool Executor
│   │   │
│   │   └── llm/                    # LLM Integration
│   │       ├── __init__.py
│   │       ├── client.py           # OpenRouter Client
│   │       ├── prompts.py          # System Prompts
│   │       └── extraction.py       # Use Case Extraction
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_use_cases.py
│   │   └── test_agent.py
│   │
│   └── data/
│       ├── seed/
│       │   ├── industries.json
│       │   ├── companies.json
│       │   └── users.json
│       └── app.db                  # SQLite DB (gitignored)
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── client.ts           # API Client
│       ├── components/
│       │   ├── Layout.tsx
│       │   ├── UseCaseList.tsx
│       │   ├── UseCaseDetail.tsx
│       │   ├── UseCaseForm.tsx
│       │   ├── TranscriptUpload.tsx
│       │   └── ChatPanel.tsx
│       ├── pages/
│       │   ├── LoginPage.tsx
│       │   ├── DashboardPage.tsx
│       │   └── UseCasePage.tsx
│       ├── context/
│       │   └── AuthContext.tsx
│       └── types/
│           └── index.ts
│
└── data/
    └── transcripts/
        └── stadtwerke-workshop-2026-01.txt
```

---

## Deployment (Lokal)
### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    volumes:
      - ./backend/data:/app/data
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000
```

### Startup-Sequenz
```bash
# 1. Environment konfigurieren
cp .env.example .env
# API-Key eintragen

# 2. Starten
docker-compose up --build

# 3. Seed-Daten laden (einmalig)
docker-compose exec backend python -m app.seed

# 4. Öffnen
# Backend: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

---

## Logging-Strategie
### Format
```json
{
  "timestamp": "2026-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "app.llm.client",
  "message": "LLM request completed",
  "request_id": "abc-123",
  "data": {
    "model": "anthropic/claude-3-haiku",
    "tokens_in": 1500,
    "tokens_out": 500,
    "latency_ms": 1200
  }
}
```

### Log-Levels
| Level | Verwendung |
|-------|------------|
| DEBUG | Entwicklungs-Details |
| INFO | LLM-Calls, Tool-Executions, wichtige Events |
| WARNING | Retries, degraded performance |
| ERROR | Fehler, die behandelt wurden |
| CRITICAL | Systemfehler, die Aufmerksamkeit erfordern |