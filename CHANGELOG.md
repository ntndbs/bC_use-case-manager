# Changelog
Fortschrtit dokumentiert nach Meilensteinen. Jeder Meilenstein entspricht einem funktionsfähigen Zwischenstand.

## Legende
- 🔲 Geplant
- 🚧 In Arbeit
- ✅ Abgeschlossen

---

## M0 - Projektsetup & Dokumentation ✅
> **Ziel:** Repository bereit, Dokumentation vollständig, Issues angelegt
| Task | Status | Issue |
|------|--------|-------|
| Repository erstellen | ✅ | - |
| Dokumentationsstruktur anlegen | ✅ | - |
| Epics/Use Cases als GitHub Issues | ✅ | - |
| .gitignore, .env.example | ✅ | - |

**Checkpoint:** Alle Docs vorhanden, Issues angelegt, ready for code.

---

## M1 - Kern-Flow E2E (ohne UI) ✅
> **Ziel:** Transkript hochladen → LLM extrahiert Use Cases → in DB gespeichert
| Task | Status | Issue |
|------|--------|-------|
| Docker + FastAPI Skeleton | ✅ | - |
| SQLAlchemy Models | ✅ | #1 |
| Pydantic Schemas | ✅ | #1 |
| Seed-Daten (Industries, Companies) | ✅ | #1 |
| Transkript-Upload Endpoint | ✅ | remove DB row if file write fails |
| OpenRouter Client + Logging | ✅ | - |
| LLM-Extraktion mit Schema-Validierung | ✅ | - |
| Use Cases persistieren | ✅ | - |

**Checkpoint:** `curl` Upload → Use Cases in DB sichtbar via `sqlite3`

---

## M2 - Use Case CRUD API ✅🚧
> **Ziel:** Vollständige REST-API für Use Cases
| Task | Status | Issue |
|------|--------|-------|
| GET /use-cases (Liste + Filter) | ✅ | - |
| GET /use-cases/{id} | ✅ | - |
| POST /use-cases | ✅ | - |
| PATCH /use-cases/{id} | ✅ | - |
| DELETE /use-cases/{id} (Soft Delete / Archive) | ✅ | - |
| Status-Änderung validieren | ✅ | - |
| Restore /use-cases/{id}/restore (Archive -> New) | ✅ | - |

**Checkpoint:** Swagger UI unter `/docs` zeigt alle Endpoints; CRUD funktioniert.

---

## M3 - Agent mit Tools ✅🚧
> **Ziel:** Chat-Interface mit funktionierenden Tools
| Task | Status | Issue |
|------|--------|-------|
| Tool-Calling Loop implementieren | ✅ | #TBD |
| Tool: list_use_cases | ✅ | #TBD |
| Tool: get_use_case | ✅ | #TBD |
| Tool: create_use_case | ✅ | #TBD |
| Tool: update_use_case | ✅ | #TBD |
| Tool: set_status | ✅ | #TBD |
| Tool: archive_use_case | ✅ | #TBD |
| Tool: analyze_transcript | ✅ | #TBD |
| Tool: list_companies | ✅| #TBD |
| Chat-Endpoint POST /chat | ✅ | #TBD |
| Disambiguation bei Mehrdeutigkeit | ✅ | #TBD |

**Checkpoint:** Chat funktioniert via curl/Postman; alle Tools aufrufbar.

---

## M4 - Frontend Kern ✅
> **Ziel:** Web-UI für Use-Case-Verwaltung + Chat
| Task | Status | Issue |
|------|--------|-------|
| React + Vite + Tailwind Setup | ✅ | - |
| API-Client (fetch wrapper) | ✅ | - |
| Use-Case-Liste Komponente | ✅ | - |
| Use-Case-Detail Komponente | ✅ | - |
| Use-Case-Edit Formular | ✅ | - |
| Transkript-Upload Komponente | ✅ | - |
| Chat-Panel Komponente | ✅ | Teilweise falsche Antworten, prüfen |
| Refetch nach Agent-Aktion | ✅ | - |

**Checkpoint:** Vollständiger Flow im Browser sichtbar (noch ohne Login).

---

## M5 - Auth & RBAC 🚧
> **Ziel:** Login + Rollenbasierte Zugriffskontrolle
| Task | Status | Issue |
|------|--------|-------|
| User-Model + Password-Hashing | ✅ | - |
| POST /auth/register | ✅ | - |
| POST /auth/login (JWT) | ✅ | - |
| GET /auth/me | ✅ | - |
| JWT-Middleware | ✅ | #TBD |
| RBAC-Decorator für API-Endpoints | ✅ | - |
| RBAC-Check im Agent | ✅ | - |
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