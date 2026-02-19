# 1. Scope: Problemstatement, Ziele & Abgrenzung
## Problemstatement
Der BadenCampus führt Workshops mit verschiedenen Unternehmen aus unterschiedlichen Branchen durch. In diesen Workshops entstehen Use-Case-Ideen, die aktuell:
- **Nicht systematisch erfasst** werden (verstreut in Notizen, Protokollen, Transkripten)
- **Nicht zentral verwaltbar** sind (kein einheitliches System)
- **Nicht effizient durchsuchbar** sind (natürliche Sprache vs. strukturierte Daten)
- **Keinem definierten Prozess** folgen (Status, Bewertung, Priorisierung)

### Kernproblem
Workshop-Transkripte enthalten wertvolle Use-Case-Ideen, die manuell extrahiert werden müssten. Das ist zeitaufwändig, fehleranfällig und nicht skalierbar.

### Gewünschter Zustand
Ein zentrales System, das:
1. Use Cases **automatisch aus Transkripten extrahiert** (KI-gestützt)
2. Diese **strukturiert speichert** (Datenbank mit Relationen)
3. **Natürlichsprachliche Abfragen** ermöglicht (Agent/Chat)
4. **Standard-CRUD** über UI bereitstellt (für manuelle Verwaltung)
5. **Rollen und Berechtigungen** durchsetzt (wer darf was)

---

## Ziele (In Scope)
### Funktionale Ziele

| ID | Ziel | Priorität |
|----|------|-----------|
| Z1 | Transkript-Upload + automatische Use-Case-Extraktion via LLM | Must |
| Z2 | Strukturierte Erfassung: Titel, Beschreibung, Stakeholder, Nutzen | Must |
| Z3 | Zuordnung zu Unternehmen + Branche | Must |
| Z4 | Use Case CRUD (Create, Read, Update, (Archive,) Delete) | Must |
| Z5 | Status-Management mit definiertem Statusmodell | Must |
| Z6 | Agent/Chat als primäre Interaktionsform | Must |
| Z7 | Web-UI für Übersicht und manuelle Verwaltung | Must |
| Z8 | Registrierung und Authentifizierung (Login) | Must |
| Z9 | Rollenbasierte Berechtigungen (Reader, Maintainer, Admin) | Must |
| Z10 | RBAC gilt für UI UND Agent konsistent | Must |

### Nicht-funktionale Ziele

| ID | Ziel | Priorität |
|----|------|-----------|
| NFZ1 | Lokal startbar mit 1-2 Kommandos | Must |
| NFZ2 | Saubere README mit Setup-Anleitung | Must |
| NFZ3 | Dokumentierte Architektur und Entscheidungen | Must |
| NFZ4 | Robuste LLM-Ausgaben (Schema-Validierung, Retry) | Must |
| NFZ5 | Strukturiertes Logging für LLM- und Tool-Calls | Must |
| NFZ6 | Keine Secrets im Repository | Must |

---

## Nicht-Ziele (Out of Scope)

Folgende Features sind in der Aufgabenstellung erwähnt, aber **explizit nicht Teil des MVP**:

| Feature | Kategorie | Begründung für Ausschluss |
|---------|-----------|---------------------------|
| Use-Case-Beziehungen / Abhängigkeiten | Should-Have | Erfordert komplexe Datenmodellierung + UI |
| Branchenübergreifende Intelligenz | Should-Have | Benötigt Embedding-Infrastruktur / Similarity Search |
| ~~Bewertungs- und Priorisierungssystem~~ | ~~Should-Have~~ | **Nachträglich umgesetzt** — 5 Bewertungsdimensionen (1-5) + Durchschnitt |
| Roadmap-Generierung | Nice-to-Have | Abhängig von Priorisierung; hohe Komplexität |
| Visualisierungen / Graphen / Dashboards | Nice-to-Have | Hoher UI-Aufwand; kein E2E-Mehrwert |
| Multi-Transkript-Deduplizierung | Nice-to-Have | Edge Case; erfordert Similarity Matching |
| Echtzeit-Sync via WebSocket | Nice-to-Have | Polling/Refetch reicht für Demo |
| Enterprise-Security (SSO, MFA, Audit) | - | Über Prototyp-Scope hinaus |
| Multi-Tenancy | - | Nicht gefordert |

### Begründung der Priorisierung
**Prinzip:** "Working End-to-End schlägt Feature-Breite"
Ein stabiler Kern-Flow (Transkript → Use Cases → Verwaltung via Chat + UI) ist wertvoller als viele halbfertige Features. Die Should-Have und Nice-to-Have Features können in einer späteren Iteration hinzugefügt werden.

---

## Erfolgskriterien
Der Prototyp ist erfolgreich, wenn folgende Demo in **unter 3 Minuten** durchführbar ist:
| Schritt | Aktion | Erwartetes Ergebnis |
|---------|--------|---------------------|
| 1 | Login als Maintainer | Zugang zum System |
| 2 | Transkript hochladen (UI oder Chat) | Datei wird angenommen, Use Cases automatisch extrahiert |
| 3 | Use Cases ansehen | Extrahierte Use Cases in Liste sichtbar |
| 4 | Agent fragen: "Zeige alle Use Cases" | Agent antwortet mit Liste |
| 5 | Agent: "Setze Use Case #1 auf In Bewertung" | Status wird geändert |
| 6 | UI prüfen | Statusänderung ist sichtbar |
| 7 | Use Case bewerten (1-5 Sterne) | Bewertung wird gespeichert, Durchschnitt berechnet |
| 8 | Als Reader einloggen | Anderer Zugang |
| 9 | Versuch zu editieren | Wird verhindert (UI + Agent) |

---

## Abgrenzung: Was dieses System ist und nicht ist
### Es IST:
- Eine **Use Case Library** mit KI-Unterstützung
- Ein **Prototyp/PoC** zur Demonstration des Konzepts
- **Agent-first**: Chat als primäre Interaktionsform
- **Lokal lauffähig** für Demo-Zwecke

### Es ist NICHT:
- Ein **Projektmanagement-Tool** (wie Jira, Asana)
- Ein **Issue-Tracker** (wie GitHub Issues)
- Eine **produktionsreife Lösung** (Security, Skalierung, etc.)
- Ein **Ersatz für menschliche Analyse** (LLM-Output muss reviewt werden)

---

## Stakeholder
| Rolle | Interesse | Einfluss auf Scope |
|-------|-----------|-------------------|
| BadenCampus (Auftraggeber) | Bewertung der technischen Fähigkeiten | Anforderungen definiert |
| Reviewer | Nachvollziehbarkeit, Code-Qualität | Bewertungskriterien |
| Entwickler (ich) | Machbarkeit in 5 Tagen | Priorisierung |
| Endnutzer (fiktiv) | Einfache Bedienung | Implizite UX-Anforderungen |