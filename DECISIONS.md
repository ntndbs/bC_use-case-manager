# Entscheidungen & Trade-offs
Dokumentation aller wesentlichen Architektur- und Scope-Entscheidungen mit Begründung.
Siehe auch: [04-ARCHITECTURE.md](docs/04-ARCHITECTURE.md) für den vollständigen Tech-Stack und das Datenmodell.

---

## Technologie-Entscheidungen
### T1: Eigenes Tool-Calling statt LangChain ✅
**Entscheidung:** Custom Implementation mit OpenRouter Function Calling
**Alternativen betrachtet:**
| Option | Pro | Contra |
|--------|-----|--------|
| LangChain | Schneller Start, viele Beispiele | Magie, schwer zu debuggen, Overhead, Zeit-Risiko |
| LlamaIndex | Gute RAG-Features | Overkill für diesen Use Case |
|**Eigenes Tool-Calling** | Volle Kontrolle, transparent, reviewer-freundlich | Mehr initialer Code |

**Begründung:**
- OpenRouter unterstützt natives Function Calling (OpenAI-kompatibel)
- ~150 LOC für robusten Agent-Loop
- Reviewer sieht exakt, was passiert (kein Framework-Magie)
- Volle Kontrolle über Retry-Logik, Logging, Error Handling

**Trade-off:** Mehr Boilerplate, aber bessere Nachvollziehbarkeit.

---

### T2: SQLite statt PostgreSQL ✅
**Entscheidung:** SQLite für MVP
**Begründung:**
- Zero-Config Setup (keine zusätzlichen Container)
- Ausreichend für Demo-Szenario (kein Multi-User-Concurrent-Access)
- SQLAlchemy abstrahiert; Migration zu PostgreSQL trivial

**Trade-off:** Keine echte Concurrency – irrelevant für lokalen Prototyp.

---

### T3: Personen als JSON statt eigene Entity ✅
**Entscheidung:** `stakeholders` als JSON-Array im UseCase
```json
{
  "stakeholders": [
    {"name": "Max Müller", "role": "Vertriebsleiter"},
    {"name": "Anna Schmidt", "role": "IT-Leiterin"}
  ]
}
```

**Alternativen betrachtet:**
- Separate `Person`-Tabelle mit m:n-Relation zu UseCase
- Normalisiertes Modell mit Deduplizierung

**Begründung:**
- Spart 2 Tabellen + Join-Logik + zusätzliche Endpoints
- Transkript-Extraktion liefert ohnehin unstrukturierte Namen
- Für MVP ausreichend; Schema erlaubt spätere Migration

**Trade-off:** Keine Deduplizierung von Personen über Use Cases hinweg.

---

### T4: Polling statt WebSocket ✅
**Entscheidung:** Frontend pollt/refetcht nach Agent-Aktionen
**Begründung:**
- WebSocket-Setup kostet ~2h (Backend + Frontend + State-Sync)
- Polling mit manuellem Refetch ist für Demo ausreichend
- Einfacher zu debuggen

**Trade-off:** Nicht "instant", aber akzeptabel für MVP.

---

### T5: Tech-Stack ✅
**Entscheidung:**
- Backend: Python 3.11 + FastAPI
- Frontend: React 19 + TypeScript + Tailwind CSS
- Datenbank: SQLite (via SQLAlchemy)
- LLM: OpenRouter API

**Begründung:**
- FastAPI: Schnell, typisiert, automatische OpenAPI-Docs
- React/TS: Industriestandard, gute Tooling
- Tailwind: Schnelles Styling ohne CSS-Dateien
- SQLite: Zero-Config für lokalen Prototyp

---

## Scope-Entscheidungen
Siehe auch: [01-SCOPE.md](docs/01-SCOPE.md) für Ziele und Nicht-Ziele.

### S1: MVP-Fokus auf E2E-Flow ✅
**Entscheidung:** Working End-to-End schlägt Feature-Breite
**Konsequenz:** Folgende Features sind explizit Out-of-Scope:
- Use-Case-Beziehungen / Abhängigkeitsgraphen (→ E9 (#121), geplant)
- Branchenübergreifende Intelligenz / Ähnlichkeitssuche (→ E13 (#125), geplant)
- Roadmap-Generierung (→ E11 (#123), geplant)
- Visualisierungen / Dashboards (→ E14 (#126), geplant)
- Multi-Transkript-Deduplizierung (→ E12 (#124), geplant)
- Echtzeit-Sync via WebSocket

**Update:** Bewertungssystem (5 Dimensionen: Effort, Benefit, Feasibility, Data Availability, Strategic Relevance) wurde nachträglich implementiert — nicht mehr Out-of-Scope.

**Begründung:** Jedes der verbleibenden Features erhöht Komplexität signifikant, ohne den Kern-Wertnachweis zu verbessern.

---

### S2: Auth später, aber vorbereitet ✅
**Entscheidung:** RBAC-Struktur von Anfang an im Code, Enforcement in späterem Meilenstein
**Begründung:**
- Kern-Flow (Extraktion) kann ohne Auth entwickelt werden
- Frühe RBAC-Enforcement würde Development verlangsamen
- Vorbereitung (Role-Enum, User-Model) ermöglicht einfaches Aktivieren

**Update:** Auth & RBAC vollständig implementiert (E6 ✅). 3-Rollen-Modell (Reader, Maintainer, Admin) mit JWT-Auth auf allen Endpoints + RBAC pro Agent-Tool.

---

## Annahmen
| ID | Annahme | Auswirkung wenn falsch |
|----|---------|------------------------|
| A1 | Nur synthetische Testdaten | Datenschutz-Anforderungen steigen drastisch |
| A2 | Nur lokaler Betrieb | Security-Anforderungen steigen |
| A3 | OpenRouter ist verfügbar und stabil | Fallback: Manuelles Use-Case-Anlegen |
| A4 | Kein Multi-User gleichzeitig | Keine Concurrency-Konflikte |
| A5 | Transkripte sind <50k Tokens | Sonst: Chunking erforderlich |
| A6 | 1-15 Use Cases pro Transkript | Pagination bei Bedarf |

---

## Entschiedene Design-Fragen
| ID | Thema | Entscheidung | Begründung |
|----|-------|-------------|------------|
| O1 | LLM-Modell | Claude 3 Haiku via OpenRouter | Schnell, günstig, ausreichend für Extraktion |
| O2 | Chat-UI Position | Sidebar (rechts, ausklappbar) | Immer erreichbar, blockiert nicht die Hauptansicht |
| O3 | Status-Übergänge | Eingeschränkt (definierte Transitions) | Verhindert ungültige Zustände, z.B. `new → completed` |