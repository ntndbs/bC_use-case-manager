# 3. Datenlage & Testdaten
## Ist-Situation
**Verfügbare echte Daten:** Keine.
Der Auftraggeber (BadenCAMPUS) hat auf Nachfrage bestätigt, dass keine echten Workshop-Transkripte oder Use-Case-Daten zur Verfügung gestellt werden.
**Konsequenz:** Wir arbeiten ausschließlich mit synthetischen Testdaten.

---

## Strategie: Synthetische Testdaten
Wir generieren realistische, aber vollständig fiktive Daten für:
1. **Stammdaten** (Industries, Companies)
2. **Benutzer** (für Auth-Tests)
3. **Transkripte** (Workshop-Simulationen)
4. **Use Cases** (optional, für initiale Demo)

---

## Stammdaten (Seed)
### Industries
| ID | Name | Beschreibung |
|----|------|--------------|
| 1 | Energieversorgung | Stadtwerke, Netzbetreiber, erneuerbare Energien |
| 2 | Maschinenbau | Produktionsunternehmen, Anlagenbau |
| 3 | Gesundheitswesen | Kliniken, Medizintechnik, Pflege |

### Companies
| ID | Name | Industry | Beschreibung |
|----|------|----------|--------------|
| 1 | Stadtwerke Musterstadt GmbH | Energieversorgung | Regionaler Energieversorger |
| 2 | Müller Maschinenbau AG | Maschinenbau | Mittelständischer Maschinenbauer |
| 3 | Klinikum Schwarzwald | Gesundheitswesen | Regionales Krankenhaus |

### Users (Test-Accounts)
| Email | Passwort (Klartext) | Rolle | Zweck |
|-------|---------------------|-------|-------|
| admin@example.com | admin123 | ADMIN | Admin-Funktionen testen |
| maintainer@example.com | maintain123 | MAINTAINER | CRUD-Operationen testen |
| reader@example.com | reader123 | READER | Read-Only-Zugriff testen |

⚠️ **Nur für lokale Entwicklung.** Passwörter werden gehasht gespeichert. Diese Accounts dienen ausschließlich dem Testen.

---

## Synthetische Transkripte
### Anforderungen an Transkripte
Ein gutes Test-Transkript muss:
1. **Realistische Workshop-Struktur** haben
2. **Erkennbare Use Cases** enthalten (3-5 pro Transkript)
3. **Personen mit Rollen** benennen
4. **Branchenbezug** aufweisen
5. **Variierenden Detailgrad** bieten (manche Use Cases klar, manche vage)

### Workshop-Struktur (Template)
```
1. Begrüßung + Vorstellungsrunde (~5%)
2. Problemdiskussion / Status Quo (~20%)
3. Ideengenerierung - hier entstehen Use Cases (~50%)
4. Diskussion / Priorisierung (~20%)
5. Abschluss / nächste Schritte (~5%)
```

### Signalwörter für Use Cases
Das LLM soll Use Cases anhand folgender Signale erkennen:
- "Wir könnten...", "Eine Idee wäre...", "Anwendungsfall wäre..."
- "Use Case:", "Anwendungsfall:", "Möglichkeit:"
- "Das würde uns helfen bei...", "Damit könnten wir..."
- "Ich stelle mir vor, dass...", "Stellt euch vor, wir hätten..."

### Personen-Format
```
Name (Rolle im Unternehmen)
Beispiel: Dr. Maria Schmidt (Geschäftsführerin)
```

### Transkript-Spezifikationen
| Eigenschaft | Wert |
|-------------|------|
| Sprache | Deutsch |
| Länge | 2.000 - 5.000 Wörter |
| Format | Plain Text (.txt) |
| Encoding | UTF-8 |
| Use Cases pro Transkript | 3-5 |
| Teilnehmer pro Workshop | 3-5 |

---

## Beispiel-Transkript (Auszug)

```
================================================================================
WORKSHOP-TRANSKRIPT
================================================================================
Unternehmen: Stadtwerke Musterstadt GmbH
Branche: Energieversorgung
Datum: 15.01.2026
Ort: BadenCampus, Freiburg

Teilnehmer:
- Dr. Maria Schmidt (Geschäftsführerin)
- Thomas Weber (Leiter IT)
- Sandra Hoffmann (Leiterin Kundenservice)
- Michael Braun (Teamleiter Netzplanung)

Moderation: Lisa Berger (BadenCampus)
================================================================================

[00:00:00 - Begrüßung]

Lisa Berger: Herzlich willkommen zum KI-Workshop. Heute wollen wir gemeinsam 
herausfinden, wo künstliche Intelligenz bei den Stadtwerken Musterstadt 
konkret Mehrwert schaffen kann. Beginnen wir mit einer kurzen Vorstellungsrunde.

Dr. Maria Schmidt: Gerne. Ich bin Maria Schmidt, seit fünf Jahren 
Geschäftsführerin der Stadtwerke. Mein Fokus liegt auf der strategischen 
Ausrichtung, insbesondere Digitalisierung und Nachhaltigkeit.

[...]

[00:15:00 - Problemdiskussion]

Sandra Hoffmann: Im Kundenservice haben wir ein großes Problem. Unsere 
Mitarbeiter beantworten täglich die gleichen Fragen - zu Tarifen, 
Abschlagszahlungen, Zählerständen. Das bindet enorm viel Kapazität.

Thomas Weber: Das bestätigen auch unsere Zahlen. Etwa 60% der Anfragen 
sind Standardfragen, die theoretisch automatisiert beantwortet werden könnten.

[00:18:00 - Ideengenerierung]

Lisa Berger: Das klingt nach einem konkreten Ansatzpunkt. Wie könnte eine 
KI-Lösung hier aussehen?

Thomas Weber: Eine Idee wäre ein KI-Chatbot, der die Standard-Kundenanfragen 
automatisch beantwortet. Use Case wäre also: Automatische Beantwortung von 
wiederkehrenden Kundenanfragen zu Tarifen, Rechnungen und Zählerständen.

Sandra Hoffmann: Genau. Der erwartete Nutzen wäre enorm. Ich schätze, wir 
könnten 40-50% der Anfragen automatisieren. Das würde etwa 2 FTE freisetzen, 
die sich dann um komplexere Kundenanliegen kümmern können.

Dr. Maria Schmidt: Das passt auch zu unserer Strategie. Wir wollen den 
Service verbessern, nicht Personal abbauen. Die freiwerdende Kapazität 
würde in Beratung fließen.

[00:25:00]

Michael Braun: Ich hätte noch einen Anwendungsfall aus dem Netzbereich. 
Wir machen aktuell viel manuelle Netzplanung. Mit KI könnten wir 
Lastprognosen erstellen und das Netz vorausschauend optimieren.

Lisa Berger: Können Sie das konkretisieren?

Michael Braun: Use Case: KI-gestützte Lastprognose für das Stromnetz. 
Die KI analysiert historische Verbrauchsdaten, Wetterdaten und Events, 
um den Strombedarf vorherzusagen. Stakeholder wären Netzplanung und 
Einkauf. Nutzen: bessere Einkaufskonditionen, weniger Ausgleichsenergie.

[...]
```

---

## Generierungsmethode
| Option | Pro | Contra | Entscheidung |
|--------|-----|--------|--------------|
| **A: Manuell erstellen** | Volle Kontrolle, optimale Qualität | Zeitaufwand (~1h pro Transkript) | ✅ Für Haupt-Demo |
| **B: LLM-generiert** | Schnell, mehrere Varianten | Muss reviewt werden, ggf. inkonsistent | Optional für Tests |

**Entscheidung:** 
- 1 manuell erstelltes Haupt-Transkript (Energiebranche) für Demo
- Optional: 1-2 LLM-generierte Transkripte für andere Branchen

---

## Datei-Struktur

```
data/
├── seed/
│   ├── industries.json      # Branchen
│   ├── companies.json       # Unternehmen
│   └── users.json           # Test-Accounts (werden beim Seed gehasht)
└── transcripts/
    ├── stadtwerke-workshop-2026-01.txt    # Haupt-Demo (manuell)
    ├── maschinenbau-workshop-2026-01.txt  # Optional
    └── klinikum-workshop-2026-01.txt      # Optional
```

---

## Regeln für synthetische Daten

| Regel | Begründung |
|-------|------------|
| Keine echten Firmennamen | Verwechslung/Haftung vermeiden |
| Keine echten Personennamen | DSGVO-Konformität auch bei Testdaten |
| Realistische, aber fiktive Inhalte | Demo-Qualität ohne Compliance-Risiko |
| Deutsche Sprache | Aufgabenstellung ist deutsch |
| UTF-8 Encoding | Umlaute korrekt verarbeiten |
| Konsistente Namenskonvention | Bessere Nachvollziehbarkeit |

---

## Seed-Daten Format
### industries.json
```json
[
  {
    "id": 1,
    "name": "Energieversorgung",
    "description": "Stadtwerke, Netzbetreiber, erneuerbare Energien"
  },
  {
    "id": 2,
    "name": "Maschinenbau",
    "description": "Produktionsunternehmen, Anlagenbau"
  },
  {
    "id": 3,
    "name": "Gesundheitswesen",
    "description": "Kliniken, Medizintechnik, Pflege"
  }
]
```

### companies.json
```json
[
  {
    "id": 1,
    "name": "Stadtwerke Musterstadt GmbH",
    "industry_id": 1
  },
  {
    "id": 2,
    "name": "Müller Maschinenbau AG",
    "industry_id": 2
  },
  {
    "id": 3,
    "name": "Klinikum Schwarzwald",
    "industry_id": 3
  }
]
```

### users.json
```json
[
  {
    "email": "admin@example.com",
    "password": "admin123",
    "role": "ADMIN"
  },
  {
    "email": "maintainer@example.com",
    "password": "maintain123",
    "role": "MAINTAINER"
  },
  {
    "email": "reader@example.com",
    "password": "reader123",
    "role": "READER"
  }
]
```

⚠️ Passwörter werden beim Seeding gehasht und **niemals** im Klartext gespeichert.

---

## Nächste Schritte
- [ ] Haupt-Transkript vollständig ausschreiben
- [ ] Seed-JSON-Dateien erstellen
- [ ] Seed-Script implementieren