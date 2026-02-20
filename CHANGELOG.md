# Changelog
Fortschritt dokumentiert nach Meilensteinen. Jeder Meilenstein entspricht einem funktionsfähigen Zwischenstand.

## Legende
- 🔲 Geplant
- 🚧 In Arbeit
- ✅ Abgeschlossen

---

## M0 - Projektsetup & Dokumentation ✅
**Ziel:** Repository bereit, Dokumentation vollständig, Domänenmodell definiert
**Epic(s):** E4: Domänenmodell ([#1](https://github.com/ntndbs/bC_use-case-manager/issues/1))
| Task | Status | Issue |
|------|--------|-------|
| Repository erstellen | ✅ | - |
| Dokumentationsstruktur anlegen | ✅ | - |
| Epics/Use Cases als GitHub Issues | ✅ | - |
| .gitignore, .env.example | ✅ | - |
| Industry CRUD | ✅ | [#15](https://github.com/ntndbs/bC_use-case-manager/issues/15) |
| Company CRUD | ✅ | [#16](https://github.com/ntndbs/bC_use-case-manager/issues/16) |
| Transcript speichern | ✅ | [#17](https://github.com/ntndbs/bC_use-case-manager/issues/17) |
| Seed-Daten | ✅ | [#18](https://github.com/ntndbs/bC_use-case-manager/issues/18) |

**Checkpoint:** Alle Docs vorhanden, Issues angelegt, Domänenmodell definiert.

---

## M1 - Kern-Flow E2E (ohne UI) ✅
**Ziel:** Transkript hochladen → LLM extrahiert Use Cases → in DB gespeichert
**Epic(s):** E1: Transkript-Analyse ([#2](https://github.com/ntndbs/bC_use-case-manager/issues/2))
| Task | Status | Issue |
|------|--------|-------|
| Transkript hochladen | ✅ | [#19](https://github.com/ntndbs/bC_use-case-manager/issues/19) |
| Use Cases extrahieren | ✅ | [#20](https://github.com/ntndbs/bC_use-case-manager/issues/20) |
| Extraktion validieren | ✅ | [#21](https://github.com/ntndbs/bC_use-case-manager/issues/21) |
| Use Cases persistieren | ✅ | [#22](https://github.com/ntndbs/bC_use-case-manager/issues/22) |
| Extraktion via Agent | ✅ | [#23](https://github.com/ntndbs/bC_use-case-manager/issues/23) |

**Checkpoint:** `curl` Upload → Use Cases in DB sichtbar via `sqlite3`

---

## M2 - Use Case CRUD API ✅
**Ziel:** Vollständige REST-API für Use Cases
**Epic(s):** E2: Use Case CRUD ([#3](https://github.com/ntndbs/bC_use-case-manager/issues/3))
| Task | Status | Issue |
|------|--------|-------|
| Use Cases auflisten | ✅ | [#8](https://github.com/ntndbs/bC_use-case-manager/issues/8) |
| Use Case Detail | ✅ | [#9](https://github.com/ntndbs/bC_use-case-manager/issues/9) |
| Use Case erstellen | ✅ | [#10](https://github.com/ntndbs/bC_use-case-manager/issues/10) |
| Use Case bearbeiten | ✅ | [#11](https://github.com/ntndbs/bC_use-case-manager/issues/11) |
| Status ändern | ✅ | [#12](https://github.com/ntndbs/bC_use-case-manager/issues/12) |
| Use Case archivieren | ✅ | [#13](https://github.com/ntndbs/bC_use-case-manager/issues/13) |
| Use Case wiederherstellen | ✅ | [#14](https://github.com/ntndbs/bC_use-case-manager/issues/14) |

**Checkpoint:** Swagger UI unter `/docs` zeigt alle Endpoints; CRUD funktioniert.

---

## M3 - Agent mit Tools ✅
**Ziel:** Chat-Interface mit funktionierenden Tools
**Epic(s):** E3: Agent ([#4](https://github.com/ntndbs/bC_use-case-manager/issues/4))
| Task | Status | Issue |
|------|--------|-------|
| Chat-Endpoint | ✅ | [#24](https://github.com/ntndbs/bC_use-case-manager/issues/24) |
| Tool: list_use_cases | ✅ | [#25](https://github.com/ntndbs/bC_use-case-manager/issues/25) |
| Tool: get_use_case | ✅ | [#26](https://github.com/ntndbs/bC_use-case-manager/issues/26) |
| Tool: create_use_case | ✅ | [#27](https://github.com/ntndbs/bC_use-case-manager/issues/27) |
| Tool: update_use_case | ✅ | [#28](https://github.com/ntndbs/bC_use-case-manager/issues/28) |
| Tool: set_status | ✅ | [#29](https://github.com/ntndbs/bC_use-case-manager/issues/29) |
| Tool: archive_use_case | ✅ | [#30](https://github.com/ntndbs/bC_use-case-manager/issues/30) |
| Tool: analyze_transcript | ✅ | [#31](https://github.com/ntndbs/bC_use-case-manager/issues/31) |
| Disambiguation | ✅ | [#32](https://github.com/ntndbs/bC_use-case-manager/issues/32) |
| Tool: list_companies | ✅ | [#33](https://github.com/ntndbs/bC_use-case-manager/issues/33) |
| Conversation Memory | ✅ | [#34](https://github.com/ntndbs/bC_use-case-manager/issues/34) |

**Checkpoint:** Chat funktioniert via curl/Postman; alle Tools aufrufbar.

---

## M4 - Frontend Kern ✅
**Ziel:** Web-UI für Use-Case-Verwaltung + Chat
**Epic(s):** E5: Frontend ([#5](https://github.com/ntndbs/bC_use-case-manager/issues/5))
| Task | Status | Issue |
|------|--------|-------|
| Use-Case-Liste | ✅ | [#35](https://github.com/ntndbs/bC_use-case-manager/issues/35) |
| Use-Case-Detail | ✅ | [#36](https://github.com/ntndbs/bC_use-case-manager/issues/36) |
| Use-Case-Edit | ✅ | [#37](https://github.com/ntndbs/bC_use-case-manager/issues/37) |
| Status-Dropdown | ✅ | [#38](https://github.com/ntndbs/bC_use-case-manager/issues/38) |
| Transkript-Upload | ✅ | [#39](https://github.com/ntndbs/bC_use-case-manager/issues/39) |
| Chat-Panel | ✅ | [#40](https://github.com/ntndbs/bC_use-case-manager/issues/40) |
| Filter/Suche | ✅ | [#41](https://github.com/ntndbs/bC_use-case-manager/issues/41) |
| Agent→UI Sync | ✅ | [#42](https://github.com/ntndbs/bC_use-case-manager/issues/42) |

**Checkpoint:** Vollständiger Flow im Browser sichtbar (noch ohne Login).

---

## M5 - Auth & RBAC ✅
**Ziel:** Login + Rollenbasierte Zugriffskontrolle
**Epic(s):** E6: Auth & RBAC ([#6](https://github.com/ntndbs/bC_use-case-manager/issues/6))
| Task | Status | Issue |
|------|--------|-------|
| User Registration | ✅ | [#43](https://github.com/ntndbs/bC_use-case-manager/issues/43) |
| User Login (JWT) | ✅ | [#44](https://github.com/ntndbs/bC_use-case-manager/issues/44) |
| Current User (GET /auth/me) | ✅ | [#45](https://github.com/ntndbs/bC_use-case-manager/issues/45) |
| RBAC API | ✅ | [#46](https://github.com/ntndbs/bC_use-case-manager/issues/46) |
| RBAC Agent | ✅ | [#47](https://github.com/ntndbs/bC_use-case-manager/issues/47) |
| RBAC UI | ✅ | [#48](https://github.com/ntndbs/bC_use-case-manager/issues/48) |
| Login-Page | ✅ | [#49](https://github.com/ntndbs/bC_use-case-manager/issues/49) |
| Admin: Rollenvergabe | ✅ | [#50](https://github.com/ntndbs/bC_use-case-manager/issues/50) |

**Checkpoint:** Reader kann nicht editieren – weder via UI noch via Agent.

---

## Test Sprint
E2E-Test durchgeführt. Ergebnisse: [06-TESTS.md](docs/06-TESTS.md)
Alle gefunden Issues & Improvements wurden (und werden im weiteren Verlauf) unter [EPIC] E8: Issues & Improvements, Issue [#56](https://github.com/ntndbs/bC_use-case-manager/issues/56) gesammelt.

---

## M6 - Polish & Abgabe 🚧
**Ziel:** Abgabe-ready, Robustheit & Observability
**Epic(s):** E7: Robustheit & Observability ([#7](https://github.com/ntndbs/bC_use-case-manager/issues/7))
| Task | Status | Issue |
|------|--------|-------|
| Input Validation | ✅ | [#53](https://github.com/ntndbs/bC_use-case-manager/issues/53) |
| Health Check | ✅ | [#54](https://github.com/ntndbs/bC_use-case-manager/issues/54) |
| Strukturiertes Logging | 🔲 | [#51](https://github.com/ntndbs/bC_use-case-manager/issues/51) |
| LLM Error Handling | 🔲 | [#52](https://github.com/ntndbs/bC_use-case-manager/issues/52) |
| Update .env.example | ✅ | [#181](https://github.com/ntndbs/bC_use-case-manager/issues/181) |
---

## M7 - MVP Pilot GoLive 🚧
**Ziel:** Produktionsreife für Pilotbetrieb
**Epic(s):** E8: Issues & Improvements ([#56](https://github.com/ntndbs/bC_use-case-manager/issues/56))
| Task | Status | Issue |
|------|--------|-------|
| Systemprompt Optimierung: list_industries | ✅ | [#166](https://github.com/ntndbs/bC_use-case-manager/issues/166) |
| Chat bleibt nach Logout/Login erhalten | ✅ | [#167](https://github.com/ntndbs/bC_use-case-manager/issues/167) |
| Systemprompt Optimierung: usecase_list Tool | ✅ | [#168](https://github.com/ntndbs/bC_use-case-manager/issues/168) |
| Transkript Upload: DB-Row bei Fehler entfernen | 🔲 | [#55](https://github.com/ntndbs/bC_use-case-manager/issues/55) |

---

## Geplante Meilensteine 🔲
Detaillierte Issues: [GitHub Issues](https://github.com/ntndbs/bC_use-case-manager/issues)

| Milestone | Thema | Epic |
|-----------|-------|--------|
| M8 | Vernetzte Use Cases & Prioritätsansichten | [#121](https://github.com/ntndbs/bC_use-case-manager/issues/121) |
| M9 | Roadmap in Minuten (Now/Next/Later) | [#123](https://github.com/ntndbs/bC_use-case-manager/issues/123) |
| M10 | Transkript-Historie & Herkunftsnachweis | [#124](https://github.com/ntndbs/bC_use-case-manager/issues/124) |
| M11 | Branchenübergreifende Intelligenz | [#125](https://github.com/ntndbs/bC_use-case-manager/issues/125) |
| M12 | Polish & Visualisierung (Stretch) | [#126](https://github.com/ntndbs/bC_use-case-manager/issues/126) |