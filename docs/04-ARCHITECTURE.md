# 4. Architektur & Tech-Stack
## Systemübersicht
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  FRONTEND                                   │
│                       React 19 + TypeScript + Tailwind                      │
│  ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────────┐    │
│  │ Login /  │ │Use Case │ │Use Case │ │Upload  │ │ User-  │ │  Chat    │    │
│  │ Register │ │  List   │ │ Detail  │ │ Page   │ │verwalt.│ │  Panel   │    │
│  └──────────┘ └─────────┘ └─────────┘ └────────┘ └────────┘ └──────────┘    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP/REST
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  BACKEND                                    │
│                            FastAPI + SQLAlchemy                             │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         API Layer (Routers)                            │ │
│  │  ┌────────┐ ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌────────┐         │ │
│  │  │ /auth  │ │/use-cases│ │/companies │ │/transcr. │ │ /chat  │         │ │
│  │  │        │ │          │ │/industries│ │          │ │        │         │ │
│  │  └────────┘ └──────────┘ └───────────┘ └──────────┘ └────────┘         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         Agent Layer (services/)                        │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │ │
│  │  │ agent.py        │  │ tool_handlers.py│  │ llm.py          │         │ │
│  │  │ (Agent Loop)    │  │ (10+ Tools)     │  │ (OpenRouter)    │         │ │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘         │ │
│  │                           ┌─────────────────┐                          │ │
│  │                           │ extraction.py   │                          │ │
│  │                           │ (UC-Extraktion) │                          │ │
│  │                           └─────────────────┘                          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                      │                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         Data Layer                                     │ │
│  │  ┌─────────────────┐  ┌─────────────────┐                              │ │
│  │  │ SQLAlchemy ORM  │  │ Pydantic Schemas│                              │ │
│  │  │ (models/)       │  │ (schemas/)      │                              │ │
│  │  └─────────────────┘  └─────────────────┘                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────┬───────────────────────────────────────┬─────────────────┘
                  │                                       │ HTTPS
                  ▼                                       ▼
┌──────────────────────────────────┐  ┌──────────────────────────────────────┐
│           DATABASE               │  │         EXTERNAL SERVICES            │
│            SQLite                │  │          OpenRouter API              │
│  ┌────────┐┌────────┐┌────────┐  │  │       (LLM: Claude 3 Haiku)          │
│  │Industry││Company ││ User   │  │  └──────────────────────────────────────┘
│  └────────┘└────────┘└────────┘  │
│  ┌──────────┐ ┌────────┐         │
│  │Transcript│ │UseCase │         │
│  └──────────┘ └────────┘         │
└──────────────────────────────────┘
```

---

## Tech-Stack
### Backend
| Komponente | Technologie | Version | Begründung |
|------------|-------------|---------|------------|
| Runtime | Python | 3.11+ | Stabil, gutes LLM-Ecosystem |
| Web Framework | FastAPI | 0.109+ | Schnell, typisiert, automatische OpenAPI-Docs |
| ORM | SQLAlchemy | 2.0+ | Industriestandard, async-fähig via aiosqlite |
| Validation | Pydantic | 2.0+ | Integriert mit FastAPI, strict typing |
| Database | SQLite + aiosqlite | 3 | Zero-Config, async-fähig, ausreichend für Prototyp |
| Auth | python-jose, passlib | - | JWT-Handling, Password-Hashing (bcrypt) |
| LLM Client | openai (AsyncOpenAI) | - | OpenAI-kompatible API für OpenRouter |
| Testing | pytest + pytest-asyncio | - | Standard für Python, async-Support für FastAPI |

### Frontend
| Komponente | Technologie | Version | Begründung |
|------------|-------------|---------|------------|
| Framework | React | 19 | Industriestandard, große Community |
| Language | TypeScript | 5+ | Type-Safety, bessere DX |
| Build Tool | Vite | 5+ | Schnell, modernes Tooling |
| Styling | Tailwind CSS | 3+ | Utility-first, schnelles Prototyping |
| Routing | react-router-dom | 7+ | Client-Side Routing mit URL-Params |
| HTTP Client | fetch (native) | - | Keine zusätzliche Dependency |
| State | React Context | - | Ausreichend für MVP, kein Redux-Overhead |

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
│ rating_effort (1-5, nullable)    │
│ rating_benefit (1-5, nullable)   │
│ rating_feasibility (1-5, null.)  │
│ rating_data_availability (1-5)   │
│ rating_strategic_relevance (1-5) │
│ company_id (FK)                  │
│ transcript_id (FK, nullable)     │
│ created_by_id (FK)               │
│ created_at                       │
│ updated_at                       │
└──────────────────────────────────┘
```

---

## API-Design
### Endpoints
| Method | Endpoint | Beschreibung | Auth | RBAC |
|--------|----------|--------------|------|------|
| POST | /auth/register | User registrieren | - | - |
| POST | /auth/login | Login, JWT erhalten | - | - |
| GET | /auth/me | Aktueller User | ✅ | Alle |
| GET | /auth/users | Alle User auflisten | ✅ | Admin |
| PATCH | /auth/users/{id} | User-Rolle ändern | ✅ | Admin |
| DELETE | /auth/users/{id} | User löschen | ✅ | Admin |
| GET | /industries | Branchen auflisten | ✅ | Alle |
| POST | /industries | Branche anlegen | ✅ | Maintainer+ |
| GET | /companies | Unternehmen auflisten | ✅ | Alle |
| POST | /companies | Unternehmen anlegen | ✅ | Maintainer+ |
| GET | /transcripts | Transkripte auflisten | ✅ | Alle |
| GET | /transcripts/{id} | Transkript mit Inhalt | ✅ | Alle |
| POST | /transcripts | Transkript hochladen + extrahieren | ✅ | Maintainer+ |
| POST | /transcripts/{id}/extract | Use Cases erneut extrahieren | ✅ | Maintainer+ |
| GET | /use-cases | Use Cases auflisten (mit Filtern) | ✅ | Alle |
| GET | /use-cases/{id} | Use Case Detail | ✅ | Alle |
| POST | /use-cases | Use Case anlegen | ✅ | Maintainer+ |
| PATCH | /use-cases/{id} | Use Case bearbeiten | ✅ | Maintainer+ |
| DELETE | /use-cases/{id} | Use Case archivieren (Soft Delete) | ✅ | Admin |
| PATCH | /use-cases/{id}/restore | Archivierten Use Case wiederherstellen | ✅ | Admin |
| DELETE | /use-cases/{id}/permanent | Use Case endgültig löschen | ✅ | Admin |
| POST | /chat | Agent-Interaktion (inkl. optionalem Datei-Upload) | ✅ | Alle (RBAC pro Tool) |

---

## Agent-Architektur
Der Agent (`services/agent.py`) implementiert eine Tool-Calling-Loop: User-Nachricht → LLM → optional Tool-Call(s) mit RBAC-Check → Ergebnis zurück an LLM → nächste Runde oder finale Antwort. Max. 10 Runden pro Request.

### Tools (13 registriert)
| Tool | Beschreibung | RBAC |
|------|-------------|------|
| list_use_cases | Use Cases auflisten (mit Filter) | Alle |
| get_use_case | Einzelnen Use Case abrufen | Alle |
| create_use_case | Use Case manuell anlegen | Maintainer+ |
| update_use_case | Use Case bearbeiten | Maintainer+ |
| set_status | Status-Übergang durchführen | Maintainer+ |
| archive_use_case | Use Case archivieren (Soft Delete) | Admin |
| restore_use_case | Archivierten Use Case wiederherstellen | Admin |
| analyze_transcript | Use Cases aus bestehendem Transkript extrahieren | Maintainer+ |
| list_companies | Unternehmen auflisten | Alle |
| list_industries | Branchen auflisten | Alle |
| create_industry | Neue Branche anlegen | Maintainer+ |
| create_company | Neues Unternehmen anlegen | Maintainer+ |
| save_transcript | Angehängtes Transkript speichern + extrahieren | Maintainer+ |

---

## Projektstruktur
```
use-case-manager/
├── .env.example              # Environment-Vorlage (API-Keys etc.)
├── requirements.txt          # Python-Dependencies
├── docs/                     # Projektdokumentation (01-06)
│   └── diagrams/             # Mermaid-Diagramme
│
├── backend/
│   ├── main.py               # FastAPI App + Startup
│   ├── seed.py               # Stammdaten laden (Industries, Companies, Users)
│   ├── api/                  # Router (auth, use_cases, companies, industries, transcripts, chat)
│   ├── core/                 # Config, Dependencies, Security (JWT, RBAC)
│   ├── db/                   # Database Connection + SQLAlchemy Models
│   ├── schemas/              # Pydantic Request/Response Schemas
│   ├── services/             # Agent (agent.py, llm.py, tool_handlers.py, extraction.py)
│   ├── tests/                # pytest (auth, use_cases, permissions, tool_handlers, extraction)
│   └── data/
│       ├── seed/             # Stammdaten-JSONs (industries, companies, users)
│       └── upload/           # Synthetische Transkripte (.txt)
│
└── frontend/
    ├── index.html
    ├── vite.config.ts
    └── src/
        ├── App.tsx            # Routing
        ├── api/               # API Client (fetch-Wrapper)
        ├── components/        # Layout, ChatPanel, UI-Komponenten
        ├── context/           # AuthContext, RefreshContext
        └── pages/             # Login, Register, UseCaseList, UseCaseDetail, Upload, Admin
```

---

## Testing
Jeder Test läuft isoliert gegen eine frische In-Memory-SQLite-DB. Auth-Helper erzeugen JWT-Header für alle drei Rollen (Reader, Maintainer, Admin).

```
backend/tests/
├── conftest.py              # Fixtures: DB, Client, Seed-Daten, Auth-Helper
├── test_auth.py             # Auth-Endpoints (Register, Login, RBAC)
├── test_use_cases.py        # Use Case CRUD + Status-Workflow
├── test_permissions.py      # RBAC pro Endpoint + Rolle
├── test_tool_handlers.py    # Agent-Tools Unit-Tests
└── test_extraction.py       # LLM-Extraktion (mit Mock)
```

---

## Logging
Standard Python `logging` Modul. Geloggt werden:
- LLM-Calls (Model, Anzahl Messages)
- Tool-Ausführungen (Name, Ergebnis)
- Fehler (LLM-Parsing, Tool-Fehler, Auth-Fehler)