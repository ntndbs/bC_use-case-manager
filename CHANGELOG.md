# Changelog
Fortschrtit dokumentiert nach Meilensteinen. Jeder Meilenstein entspricht einem funktionsfähigen Zwischenstand.

## Legende
- 🔲 Geplant
- 🚧 In Arbeit
- ✅ Abgeschlossen

---

## M0 - Projektsetup & Dokumentation 🚧
> **Ziel:** Repository bereit, Dokumentation vollständig, Issues angelegt
| Task | Status | Issue |
|------|--------|-------|
| Repository erstellen | ✅ | - |
| Dokumentationsstruktur anlegen | ✅ | - |
| Epics/Use Cases als GitHub Issues | 🔲 | - |
| .gitignore, .env.example | ✅ | - |

**Checkpoint:** Alle Docs vorhanden, Issues angelegt, ready for code.

---

## M1 - Kern-Flow E2E (ohne UI) 🔲
> **Ziel:** Transkript hochladen → LLM extrahiert Use Cases → in DB gespeichert
| Task | Status | Issue |
|------|--------|-------|
| Docker + FastAPI Skeleton | 🔲 | #TBD |
| SQLAlchemy Models | 🔲 | #TBD |
| Seed-Daten (Industries, Companies) | 🔲 | #TBD |
| Transkript-Upload Endpoint | 🔲 | #TBD |
| OpenRouter Client + Logging | 🔲 | #TBD |
| LLM-Extraktion mit Schema-Validierung | 🔲 | #TBD |
| Use Cases persistieren | 🔲 | #TBD |

**Checkpoint:** `curl` Upload → Use Cases in DB sichtbar via `sqlite3`

---

## M2 - Use Case CRUD API 🔲
> **Ziel:** Vollständige REST-API für Use Cases
| Task | Status | Issue |
|------|--------|-------|
| GET /use-cases (Liste + Filter) | 🔲 | #TBD |
| GET /use-cases/{id} | 🔲 | #TBD |
| POST /use-cases | 🔲 | #TBD |
| PATCH /use-cases/{id} | 🔲 | #TBD |
| DELETE /use-cases/{id} (Soft Delete / Archive) | 🔲 | #TBD |
| Status-Änderung validieren | 🔲 | #TBD |

**Checkpoint:** Swagger UI unter `/docs` zeigt alle Endpoints; CRUD funktioniert.

---

## M3 - Agent mit Tools 🔲
> **Ziel:** Chat-Interface mit funktionierenden Tools
| Task | Status | Issue |
|------|--------|-------|
| Tool-Calling Loop implementieren | 🔲 | #TBD |
| Tool: list_use_cases | 🔲 | #TBD |
| Tool: get_use_case | 🔲 | #TBD |
| Tool: create_use_case | 🔲 | #TBD |
| Tool: update_use_case | 🔲 | #TBD |
| Tool: set_status | 🔲 | #TBD |
| Tool: archive_use_case | 🔲 | #TBD |
| Tool: analyze_transcript | 🔲 | #TBD |
| Tool: list_companies | 🔲 | #TBD |
| Chat-Endpoint POST /chat | 🔲 | #TBD |
| Disambiguation bei Mehrdeutigkeit | 🔲 | #TBD |

**Checkpoint:** Chat funktioniert via curl/Postman; alle Tools aufrufbar.

---

## M4 - Frontend Kern 🔲
> **Ziel:** Web-UI für Use-Case-Verwaltung + Chat
| Task | Status | Issue |
|------|--------|-------|
| React + Vite + Tailwind Setup | 🔲 | #TBD |
| API-Client (fetch wrapper) | 🔲 | #TBD |
| Use-Case-Liste Komponente | 🔲 | #TBD |
| Use-Case-Detail Komponente | 🔲 | #TBD |
| Use-Case-Edit Formular | 🔲 | #TBD |
| Transkript-Upload Komponente | 🔲 | #TBD |
| Chat-Panel Komponente | 🔲 | #TBD |
| Refetch nach Agent-Aktion | 🔲 | #TBD |

**Checkpoint:** Vollständiger Flow im Browser sichtbar (noch ohne Login).

---

## M5 - Auth & RBAC 🔲
> **Ziel:** Login + Rollenbasierte Zugriffskontrolle
| Task | Status | Issue |
|------|--------|-------|
| User-Model + Password-Hashing | 🔲 | #TBD |
| POST /auth/register | 🔲 | #TBD |
| POST /auth/login (JWT) | 🔲 | #TBD |
| GET /auth/me | 🔲 | #TBD |
| JWT-Middleware | 🔲 | #TBD |
| RBAC-Decorator für API-Endpoints | 🔲 | #TBD |
| RBAC-Check im Agent | 🔲 | #TBD |
| Login-Page im Frontend | 🔲 | #TBD |
| Protected Routes | 🔲 | #TBD |
| Conditional UI (Reader vs Maintainer) | 🔲 | #TBD |

**Checkpoint:** Reader kann nicht editieren – weder via UI noch via Agent.

---

## M6 - Polish & Abgabe 🔲
> **Ziel:** Abgabe-ready, Demo in 3 Minuten möglich
| Task | Status | Issue |
|------|--------|-------|
| Error Handling vervollständigen | 🔲 | #TBD |
| Logging finalisieren (JSON-Format) | 🔲 | #TBD |
| Mindestens 3 Tests schreiben | 🔲 | #TBD |
| README mit Setup-Anleitung finalisieren | 🔲 | #TBD |
| Demo-Script schreiben | 🔲 | #TBD |
| Beispiel-Transkript finalisieren | 🔲 | #TBD |
| Finaler Self-Review | 🔲 | #TBD |

**Checkpoint:** `docker-compose up --build` → Demo in 3 Minuten durchführbar.

---

## Abgeschlossene Meilensteine
_Werden hier dokumentiert, sobald abgeschlossen._