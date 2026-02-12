# Entscheidungen & Trade-offs
Dokumentation aller wesentlichen Architektur- und Scope-Entscheidungen mit Begründung.

---

## Legende
- ✅ Entschieden
- 🔲 Offen
- ❌ Verworfen

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
- Frontend: React 18 + TypeScript + Tailwind CSS
- Datenbank: SQLite (via SQLAlchemy)
- LLM: OpenRouter API

**Begründung:**
- FastAPI: Schnell, typisiert, automatische OpenAPI-Docs
- React/TS: Industriestandard, gute Tooling
- Tailwind: Schnelles Styling ohne CSS-Dateien
- SQLite: Zero-Config für lokalen Prototyp

---

## Scope-Entscheidungen
### S1: MVP-Fokus auf E2E-Flow ✅
**Entscheidung:** Working End-to-End schlägt Feature-Breite
**Konsequenz:** Folgende Features sind explizit Out-of-Scope:
- Use-Case-Beziehungen / Abhängigkeitsgraphen
- Branchenübergreifende Intelligenz / Ähnlichkeitssuche
- Bewertungs- und Priorisierungssystem
- Roadmap-Generierung
- Visualisierungen / Dashboards
- Multi-Transkript-Deduplizierung
- Echtzeit-Sync via WebSocket

**Begründung:** Jedes dieser Features erhöht Komplexität signifikant, ohne den Kern-Wertnachweis zu verbessern.

---

### S2: Auth später, aber vorbereitet ✅
**Entscheidung:** RBAC-Struktur von Anfang an im Code, Enforcement in späterem Meilenstein
**Begründung:**
- Kern-Flow (Extraktion) kann ohne Auth entwickelt werden
- Frühe RBAC-Enforcement würde Development verlangsamen
- Vorbereitung (Role-Enum, User-Model) ermöglicht einfaches Aktivieren

---

## Annahmen
| ID | Annahme | Auswirkung wenn falsch |
|----|---------|------------------------|
| A1 | Nur synthetische Testdaten | Datenschutz-Anforderungen steigen drastisch |
| A2 | Nur lokaler Betrieb | Security-Anforderungen steigen |
| A3 | OpenRouter ist verfügbar und stabil | Fallback: Manuelles Use-Case-Anlegen |
| A4 | Kein Multi-User gleichzeitig | Keine Concurrency-Konflikte |
| A5 | Transkripte sind <50k Tokens | Sonst: Chunking erforderlich |
| A6 | 5-15 Use Cases pro Transkript | Pagination bei Bedarf |

---

## Offene Entscheidungen
_Werden während der Implementierung ergänzt._
| ID | Thema | Optionen | Status |
|----|-------|----------|--------|
| O1 | LLM-Modell für Extraktion | Haiku vs. Sonnet | 🔲 |
| O2 | Chat-UI Position | Sidebar vs. Modal vs. eigene Seite | 🔲 |
| O3 | Status-Übergangsregeln | Frei vs. eingeschränkt | 🔲 |