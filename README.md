# AI Use Case Manager
> KI-gestützter Agent zur Extraktion und Verwaltung von Use Cases aus Workshop-Transkripten.

**Status:** 🚧 In Entwicklung

## Quick Start
```bash
# 1. Repository klonen
git clone <repo-url>
cd use-case-manager

# 2. Environment konfigurieren
cp .env.example .env
# OPENROUTER_API_KEY in .env eintragen

# 3. Starten
docker-compose up --build

# 4. Öffnen
# Backend API: http://localhost:8000/docs
# Frontend: http://localhost:3000
```
> ⚠️ Setup-Anleitung wird finalisiert, sobald Implementierung abgeschlossen.

## Demo-Flow
_Wird ergänzt nach Fertigstellung._
1. Transkript hochladen
2. Use Cases ansehen
3. Agent nutzen
4. Status ändern
5. RBAC prüfen

## Dokumentation
| Dokument | Beschreibung |
|----------|--------------|
| [01-SCOPE.md](docs/01-SCOPE.md) | Problemstatement, Ziele, Nicht-Ziele |
| [02-RISKS.md](docs/02-RISKS.md) | Risiken, Compliance, Security |
| [03-DATA.md](docs/03-DATA.md) | Datenlage, synthetische Testdaten |
| [04-ARCHITECTURE.md](docs/04-ARCHITECTURE.md) | Tech-Stack, Architektur |
| [05-BACKLOG.md](docs/05-BACKLOG.md) | Epics, Use Cases, Priorisierung |
| [DECISIONS.md](DECISIONS.md) | Trade-offs, Entscheidungen |
| [CHANGELOG.md](CHANGELOG.md) | Meilensteine, Fortschritt |

## Tech Stack
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, SQLite
- **Frontend:** React 18, TypeScript, Tailwind CSS
- **LLM:** OpenRouter API (?)
- **Agent:** Custom Tool-Calling (kein Framework)

## Projektstruktur
```
├── backend/           # FastAPI Application
├── frontend/          # React Application
├── data/              # Seed-Daten, Beispiel-Transkripte
├── docs/              # Projektdokumentation
├── docker-compose.yml
├── DECISIONS.md
├── CHANGELOG.md
└── README.md
```

## Bekannte Einschränkungen
_Wird ergänzt während der Implementierung._

## Lizenz
MIT