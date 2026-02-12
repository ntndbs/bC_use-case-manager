# 5. Product Backlog
## Priorisierungs-Logik
**Prinzip:** Working E2E > Feature-Breite
### Prioritätsstufen
| Prio | Bedeutung | Kriterium |
|------|-----------|-----------|
| **Must** | Ohne das kein sinnvoller Demo-Flow | Blockiert E2E |
| **Should** | Verbessert Demo signifikant | E2E funktioniert auch ohne |
| **Could** | Nice-to-have | Nur wenn Zeit übrig |
| **Won't** | Explizit ausgeschlossen | Out of Scope für MVP |

### Implementierungs-Reihenfolge
Nach **Epic 1 + 2 + 3** existiert ein sichtbarer E2E-Flow (ohne UI).
Nach **Epic 4 + 5** ist der Flow im Browser sichtbar.
Nach **Epic 6** ist das System abgesichert (Auth + RBAC).

---

## Epic 1: Transkript-Analyse (Kern-Wertversprechen)
> Als Nutzer möchte ich ein Workshop-Transkript hochladen und automatisch strukturierte Use Cases extrahieren lassen.
| ID | Use Case | Prio | Akzeptanzkriterium | Status |
|----|----------|------|---------------------|--------|
| E1-UC1 | Transkript hochladen | Must | POST /transcripts mit .txt-Datei gibt 201 zurück | 🔲 Offen |
| E1-UC2 | Use Cases extrahieren | Must | LLM extrahiert mind. 1 Use Case mit Titel, Beschreibung, Stakeholders, Nutzen | 🔲 Offen |
| E1-UC3 | Extraktion validieren | Must | JSON-Schema-Validierung; bei Fehler: Retry (max 2x) | 🔲 Offen |
| E1-UC4 | Use Cases persistieren | Must | Extrahierte Use Cases in DB mit FK zu Transcript + Company | 🔲 Offen |
| E1-UC5 | Extraktion via Agent | Must | Chat: "Analysiere Transkript X" → Agent führt Extraktion durch | 🔲 Offen |

**Risiken:**
- LLM liefert ungültiges JSON → Mitigation: Structured Output + Retry
- Zu viele/wenige Use Cases extrahiert → Mitigation: User kann im UI korrigieren

**Abhängigkeiten:** Benötigt E4 (Domänenmodell) als Basis.

---

## Epic 2: Use Case Verwaltung (CRUD)
> Als Nutzer möchte ich Use Cases ansehen, bearbeiten und deren Status verwalten.
| ID | Use Case | Prio | Akzeptanzkriterium | Status |
|----|----------|------|---------------------|--------|
| E2-UC1 | Use Cases auflisten | Must | GET /use-cases gibt Liste zurück; Filter: company, status, search | 🔲 Offen |
| E2-UC2 | Use Case Detail | Must | GET /use-cases/{id} gibt vollständigen Use Case zurück | 🔲 Offen |
| E2-UC3 | Use Case erstellen | Must | POST /use-cases mit Pflichtfeldern; validiert Company-FK | 🔲 Offen |
| E2-UC4 | Use Case bearbeiten | Must | PATCH /use-cases/{id} für Titel, Beschreibung, Stakeholders, Benefit | 🔲 Offen |
| E2-UC5 | Status ändern | Must | PATCH /use-cases/{id} mit neuem Status | 🔲 Offen |
| E2-UC6 | Use Case archivieren | Must | DELETE /use-cases/{id} setzt Status auf ARCHIVED (Soft Delete) | 🔲 Offen |
| E2-UC7 | Use Case wiederherstellen | Should | PATCH /use-cases/{id}/restore setzt Status zurück | 🔲 Offen |

**Status-Modell:**
```
                    ┌─────────────┐
                    │    NEW      │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  IN_REVIEW  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  APPROVED   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ IN_PROGRESS │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  COMPLETED  │
                    └─────────────┘

        (ARCHIVED ist von jedem Status erreichbar)
```

---

## Epic 3: Agent / Chat-Interface
> Als Nutzer möchte ich Use Cases über natürliche Sprache verwalten.
| ID | Use Case | Prio | Akzeptanzkriterium | Status |
|----|----------|------|---------------------|--------|
| E3-UC1 | Chat-Endpoint | Must | POST /chat nimmt Message + History, gibt Agent-Response zurück | 🔲 Offen |
| E3-UC2 | Tool: list_use_cases | Must | Agent kann Use Cases auflisten mit Filtern | 🔲 Offen |
| E3-UC3 | Tool: get_use_case | Must | Agent kann einzelnen Use Case abrufen | 🔲 Offen |
| E3-UC4 | Tool: create_use_case | Must | Agent kann Use Case anlegen | 🔲 Offen |
| E3-UC5 | Tool: update_use_case | Must | Agent kann Felder ändern | 🔲 Offen |
| E3-UC6 | Tool: set_status | Must | Agent kann Status ändern | 🔲 Offen |
| E3-UC7 | Tool: archive_use_case | Must | Agent kann archivieren | 🔲 Offen |
| E3-UC8 | Tool: analyze_transcript | Must | Agent kann Transkript-Extraktion triggern | 🔲 Offen |
| E3-UC9 | Disambiguation | Must | Agent fragt nach bei mehrdeutigen Referenzen | 🔲 Offen |
| E3-UC10 | Tool: list_companies | Should | Agent kann Unternehmen auflisten | 🔲 Offen |
| E3-UC11 | Conversation Memory | Should | Agent merkt sich Kontext innerhalb einer Session | 🔲 Offen |

**Beispiel-Interaktionen:**
```
User: "Zeige mir alle Use Cases"
Agent: [list_use_cases] → "Ich habe 5 Use Cases gefunden: ..."

User: "Ändere den Status von #3 auf Genehmigt"
Agent: [set_status(id=3, status="approved")] → "Use Case #3 wurde auf 'Genehmigt' gesetzt."

User: "Ändere den Status"
Agent: "Welchen Use Case meinst du? Ich habe folgende gefunden: #1 'Chatbot', #2 'Lastprognose', ..."
```

---

## Epic 4: Domänenmodell (Company, Industry, Transcript)
> Als System brauche ich ein sauberes Datenmodell für Unternehmen, Branchen und Transkripte.
| ID | Use Case | Prio | Akzeptanzkriterium | Status |
|----|----------|------|---------------------|--------|
| E4-UC1 | Industry CRUD | Must | Branchen können angelegt/gelistet werden | 🔲 Offen |
| E4-UC2 | Company CRUD | Must | Unternehmen mit Branchenzuordnung | 🔲 Offen |
| E4-UC3 | Transcript speichern | Must | Transkript mit Content + Company-FK + Timestamp | 🔲 Offen |
| E4-UC4 | Seed-Daten | Must | 3 Industries, 3 Companies initial vorhanden | 🔲 Offen |
| E4-UC5 | DB-Migrations | Should | Alembic Setup für Schema-Änderungen | 🔲 Offen |

**Vereinfachung (dokumentiert in DECISIONS.md):**
Personen/Teilnehmer werden als JSON im UseCase gespeichert, keine separate Entity.

---

## Epic 5: Frontend
> Als Nutzer möchte ich Use Cases über eine Web-Oberfläche verwalten.
| ID | Use Case | Prio | Akzeptanzkriterium | Status |
|----|----------|------|---------------------|--------|
| E5-UC1 | Use-Case-Liste | Must | Tabelle mit Titel, Company, Status; klickbar | 🔲 Offen |
| E5-UC2 | Use-Case-Detail | Must | Vollständige Anzeige aller Felder | 🔲 Offen |
| E5-UC3 | Use-Case-Edit | Must | Formular zum Bearbeiten (nur Maintainer+) | 🔲 Offen |
| E5-UC4 | Status-Dropdown | Must | Status ändern via Dropdown | 🔲 Offen |
| E5-UC5 | Transkript-Upload | Must | Datei-Upload + Company-Auswahl | 🔲 Offen |
| E5-UC6 | Chat-Panel | Must | Sidebar/Modal für Agent-Interaktion | 🔲 Offen |
| E5-UC7 | Filter/Suche | Should | Use Cases filtern nach Company, Status, Freitext | 🔲 Offen |
| E5-UC8 | Agent→UI Sync | Should | Nach Agent-Aktion: Liste aktualisiert sich | 🔲 Offen |
| E5-UC9 | Responsive Design | Could | Mobile-taugliches Layout | 🔲 Offen |

---

## Epic 6: Auth & RBAC
> Als System möchte ich Benutzer authentifizieren und Berechtigungen durchsetzen.
| ID | Use Case | Prio | Akzeptanzkriterium | Status |
|----|----------|------|---------------------|--------|
| E6-UC1 | User Registration | Must | POST /auth/register erstellt User mit Role=READER | 🔲 Offen |
| E6-UC2 | User Login | Must | POST /auth/login gibt JWT zurück | 🔲 Offen |
| E6-UC3 | Current User | Must | GET /auth/me gibt User-Daten zurück | 🔲 Offen |
| E6-UC4 | RBAC API | Must | Endpoints prüfen Rolle; 403 bei fehlender Berechtigung | 🔲 Offen |
| E6-UC5 | RBAC Agent | Must | Agent-Tools prüfen Rolle; verweigern bei fehlendem Recht | 🔲 Offen |
| E6-UC6 | RBAC UI | Must | Edit-Buttons nur für Maintainer+ sichtbar | 🔲 Offen |
| E6-UC7 | Login-Page | Must | UI für Login | 🔲 Offen |
| E6-UC8 | Protected Routes | Must | Nicht-eingeloggte User werden zu Login redirected | 🔲 Offen |
| E6-UC9 | Admin: Rollenvergabe | Could | Admin kann User-Rollen ändern | 🔲 Offen |

**Rollen-Matrix:**
| Aktion | Reader | Maintainer | Admin |
|--------|--------|------------|-------|
| Use Cases lesen | ✅ | ✅ | ✅ |
| Use Cases suchen/filtern | ✅ | ✅ | ✅ |
| Use Cases erstellen | ❌ | ✅ | ✅ |
| Use Cases bearbeiten | ❌ | ✅ | ✅ |
| Status ändern | ❌ | ✅ | ✅ |
| Transkript hochladen | ❌ | ✅ | ✅ |
| Use Cases archivieren | ❌ | ❌ | ✅ |
| User-Rollen ändern | ❌ | ❌ | ✅ |

---

## Epic 7: Robustheit & Observability
> Als Entwickler möchte ich nachvollziehen können, was das System tut.
| ID | Use Case | Prio | Akzeptanzkriterium | Status |
|----|----------|------|---------------------|--------|
| E7-UC1 | Strukturiertes Logging | Must | JSON-Logs für LLM-Calls, Tool-Calls, Errors | 🔲 Offen |
| E7-UC2 | LLM Error Handling | Must | Timeout, Rate Limit, Invalid Response → saubere Fehlermeldung | 🔲 Offen |
| E7-UC3 | Input Validation | Must | Pydantic-Schemas für alle Endpoints | 🔲 Offen |
| E7-UC4 | Health Check | Should | GET /health gibt Status zurück | 🔲 Offen |
| E7-UC5 | Request-ID Tracking | Should | Jeder Request hat eine ID für Log-Korrelation | 🔲 Offen |

---

## Out of Scope (Won't)
Diese Features sind in der Aufgabenstellung genannt, aber **explizit nicht Teil des MVP**:
| Feature | Kategorie | Begründung |
|---------|-----------|------------|
| Use-Case-Beziehungen / Abhängigkeiten | Should-Have | Komplexe UI + Datenmodell |
| Branchenübergreifende Intelligenz | Should-Have | Erfordert Embeddings |
| Bewertung & Priorisierung | Should-Have | Zusätzliches Datenmodell |
| Roadmap-Generierung | Nice-to-Have | Abhängig von Priorisierung |
| Visualisierungen / Graphen | Nice-to-Have | Hoher UI-Aufwand |
| Multi-Transkript-Deduplizierung | Nice-to-Have | Edge Case |
| WebSocket für Realtime-Sync | Nice-to-Have | Polling reicht |
| Enterprise-Security (SSO, MFA) | - | Über MVP hinaus |
| Multi-Tenancy | - | Nicht gefordert |

---

## GitHub Issues (anzulegen)
Nach Repository-Erstellung werden folgende Issues angelegt:
### Labels
| Label | Farbe | Beschreibung |
|-------|-------|--------------|
| `epic` | #6f42c1 | Epic/Feature-Gruppe |
| `must` | #d73a4a | Priorität: Must-Have |
| `should` | #fbca04 | Priorität: Should-Have |
| `could` | #0e8a16 | Priorität: Could-Have |
| `backend` | #1d76db | Backend-Arbeit |
| `frontend` | #5319e7 | Frontend-Arbeit |
| `agent` | #f9d0c4 | Agent/LLM-Arbeit |
| `docs` | #0075ca | Dokumentation |

### Issue-Template
```markdown
## User Story
Als [Rolle] möchte ich [Funktion], damit [Nutzen].

## Akzeptanzkriterien
- [ ] Kriterium 1
- [ ] Kriterium 2

## Technische Details
- ...

## Abhängigkeiten
- Blockiert von: #X
- Blockiert: #Y
```

### Issues (Reihenfolge = Implementierungsreihenfolge)
1. **[Epic] E4: Domänenmodell** (epic, must, backend)
1a. [E4-UC1] Industry CRUD | Must | Branchen können angelegt/gelistet werden
1b. [E4-UC2] Company CRUD | Must | Unternehmen mit Branchenzuordnung|
1c. [E4-UC3] Transcript speichern | Must | Transkript mit Content + Company-FK + Upload-Timestamp
1d. [E4-UC4] Seed-Daten | Must | 3 Industries, 3 Companies initial vorhanden

2. **[Epic] E1: Transkript-Analyse** (epic, must, backend, agent)
2a. [E1-UC1] Transkript hochladen | Must | POST /transcripts mit .txt-Datei gibt 201 zurück
2b. [E1-UC2] Use Cases extrahieren | Must | LLM extrahiert mind. 1 Use Case mit Titel, Beschreibung, Stakeholders, Nutzen
2c. [E1-UC3] Extraktion validieren | Must | JSON-Schema-Validierung; bei Fehler: Retry (max 2x)
2d. [E1-UC4] Use Cases persistieren | Must | Extrahierte Use Cases in DB mit FK zu Transcript + Company
2e. [E1-UC5] Extraktion via Agent | Must | Chat: "Analysiere Transkript X" → Agent führt Extraktion durch

3. **[Epic] E2: Use Case CRUD** (epic, must, backend)
3a. [E2-UC1] Use Cases auflisten | Must | GET /use-cases gibt Liste zurück; Filter: company, status, search
3b. [E2-UC2] Use Case Detail | Must | GET /use-cases/{id} gibt vollständigen Use Case zurück
3c. [E2-UC3] Use Case erstellen | Must | POST /use-cases mit Pflichtfeldern; validiert Company-FK
3d. [E2-UC4] Use Case bearbeiten | Must | PATCH /use-cases/{id} für Titel, Beschreibung, Stakeholders, Benefit
3e. [E2-UC5] Status ändern | Must | PATCH /use-cases/{id} mit neuem Status; nur valide Übergänge
3f. [E2-UC6] Use Case archivieren | Must | DELETE /use-cases/{id} setzt Status auf ARCHIVED (kein Hard Delete)
3g. [E2-UC7] Use Case wiederherstellen | Should | PATCH /use-cases/{id}/restore setzt Status auf vorherigen Wert

4. **[Epic] E3: Agent** (epic, must, agent)
4a. [E3-UC1] Chat-Endpoint | Must | POST /chat nimmt Message, gibt Agent-Response zurück 2. [E3-UC2] Tool: list_use_cases | Must | Agent kann Use Cases auflisten mit Filtern
4b. [E3-UC3] Tool: get_use_case | Must | Agent kann einzelnen Use Case abrufen
4c. [E3-UC4] Tool: create_use_case | Must | Agent kann Use Case anlegen
4d. [E3-UC5] Tool: update_use_case | Must | Agent kann Felder ändern
4e. [E3-UC6] Tool: set_status | Must | Agent kann Status ändern
4f. [E3-UC7] Tool: archive_use_case | Must | Agent kann archivieren
4g. [E3-UC8] Tool: analyze_transcript | Must | Agent kann Transkript-Extraktion triggern
4h. [E3-UC9] Disambiguation | Must | Agent fragt nach bei mehrdeutigen Referenzen ("Meinst du [Epic] E2: Use Case CRUD #3 oder [Epic] E7: Robustheit & Observability #7?")
4i. [E3-UC10] Tool: list_companies | Should | Agent kann Unternehmen auflisten
4j. [E3-UC11] Conversation Memory | Should | Agent merkt sich Kontext innerhalb einer Session

5. **[Epic] E5: Frontend** (epic, must, frontend)
5a. [E5-UC1] Use-Case-Liste | Must | Tabelle mit Titel, Company, Status; klickbar
5b. [E5-UC2] Use-Case-Detail | Must | Vollständige Anzeige aller Felder
5c. [E5-UC3] Use-Case-Edit | Must | Formular zum Bearbeiten (nur Maintainer+)
5d. [E5-UC4] Status-Dropdown | Must | Status ändern via Dropdown
5e. [E5-UC5] Transkript-Upload | Must | Datei-Upload + Company-Auswahl
5f. [E5-UC6] Chat-Panel | Must | Sidebar/Modal für Agent-Interaktion
5g. [E5-UC7] Filter/Suche | Should | Use Cases filtern nach Company, Status, Freitext
5h. [E5-UC8] Agent→UI Sync | Should | Nach Agent-Aktion: Liste aktualisiert sich

6. **[Epic] E6: Auth & RBAC** (epic, must, backend, frontend)
6a. [E6-UC1] User Registration | Must | POST /auth/register erstellt User mit Role=READER
6b. [E6-UC2] User Login | Must | POST /auth/login gibt JWT zurück
6c. [E6-UC3] Current User | Must | GET /auth/me gibt User-Daten zurück
6d. [E6-UC4] RBAC API | Must | Endpoints prüfen Rolle; 403 bei fehlender Berechtigung
6e. [E6-UC5] RBAC Agent | Must | Agent-Tools prüfen Rolle; verweigern bei fehlendem Recht
6f. [E6-UC6] RBAC UI | Must | Edit-Buttons nur für Maintainer+ sichtbar
6g. [E6-UC7] Login-Page | Must | UI für Login
6h. [E6-UC8] Admin: Rollenvergabe | Could | Admin kann User-Rollen ändern

7. **[Epic] E7: Robustheit** (epic, should, backend)
7a. [E7-UC1] Strukturiertes Logging | Must | JSON-Logs für LLM-Calls, Tool-Calls, Errors
7b. [E7-UC2] LLM Error Handling | Must | Timeout, Rate Limit, Invalid Response → saubere Fehlermeldung
7c. [E7-UC3] Input Validation | Must | Pydantic-Schemas für alle Endpoints
7d. [E7-UC4] Health Check | Should | GET /health gibt Status zurück

---

## Testbarkeit
| Epic | Minimaler Test |
|------|----------------|
| E1 | Upload Transkript → Use Cases in DB (Integration) |
|