# 2. Risiken, Compliance & Security
## Technische Risiken
| ID | Risiko | Wahrscheinlichkeit | Impact | Mitigation | Status |
|----|--------|--------------------|--------|------------|--------|
| R1 | LLM liefert ungültiges JSON | Mittel | Hoch | JSON-Schema-Validierung + Retry (max 2x) + Fallback-Fehlermeldung | ✅ Umgesetzt |
| R2 | LLM halluziniert Use Cases | Mittel | Mittel | User-Review im UI; extrahierte Use Cases sind Vorschläge, keine Fakten | ✅ Umgesetzt |
| R3 | OpenRouter Rate Limits | Niedrig | Mittel | Exponential Backoff; strukturiertes Logging; ggf. Queueing | 🚧 Teilweise: Exponential Backoff nicht umgesetzt |
| R4 | OpenRouter Downtime | Niedrig | Hoch | Graceful Degradation: CRUD funktioniert, nur Extraktion nicht | ✅ Umgesetzt |
| R5 | Token-Kosten explodieren | Niedrig | Niedrig | Haiku-Modell (günstig); Logging pro Request; Token-Counting | 🚧 Teilweise: Token-Counting nicht umgesetzt |
| R6 | Transkript zu lang für Context Window | Niedrig | Mittel | Dateigrößen-Limit (500 KB); Ablehnung bei Überschreitung | ✅ Umgesetzt |

---

## Projektrisiken
| ID | Risiko | Mitigation |
|----|--------|------------|
| P1 | Scope Creep | Strikte Priorisierung; Won't-Liste explizit; Co-Pilot hält mich davon ab |
| P2 | Zeitdruck Tag 4-5 | E2E-Flow bis Tag 3 fertig; Tag 4-5 sind Auth + Polish |
| P3 | Unklare Anforderungen | Annahmen dokumentiert; bei Unklarheit: einfachste Interpretation |
| P4 | Technische Blockaden | Früh testen (LLM-Integration Tag 2); Fallback-Optionen definiert |

---

## Datenschutz (DSGVO-Perspektive)
### Betroffene Datenarten
| Datenart | Personenbezug | Sensibilität | Speicherort |
|----------|---------------|--------------|-------------|
| User-Accounts (Email, Passwort-Hash) | Ja | Mittel | Lokale SQLite DB |
| Transkript-Inhalte | Potenziell (Namen, Rollen) | Mittel-Hoch | Lokale DB + OpenRouter (temporär) |
| Extrahierte Stakeholder-Namen | Ja | Mittel | Lokale DB |
| Use-Case-Inhalte | Potenziell (Geschäftsgeheimnisse) | Mittel | Lokale DB |

### Annahmen für diesen Prototyp
| ID | Annahme | Konsequenz |
|----|---------|------------|
| D1 | **Keine echten Personendaten** | Wir verwenden ausschließlich synthetische Testdaten |
| D2 | **Kein Produktivbetrieb** | Prototyp läuft nur lokal für Demo-Zwecke |
| D3 | **Keine persistente Datenübermittlung** | OpenRouter verarbeitet Daten nur für API-Call |

### OpenRouter / LLM-Datenschutz
**Kritischer Punkt:** Transkript-Inhalte werden an OpenRouter gesendet. ⚠️
| Aspekt | Status | Anmerkung |
|--------|--------|-----------|
| Datenverarbeitung durch Dritte | Ja | OpenRouter + dahinterliegendes LLM-Modell |
| Verschlüsselung in Transit | Ja | HTTPS |
| Data Retention bei OpenRouter | Unklar | Müsste für Produktivbetrieb geprüft werden |
| Modell-Provider | Variabel | Je nach gewähltem Modell (Anthropic, OpenAI, etc.) |

### Für Produktivbetrieb erforderlich (nicht Prototyp/MVP)
- [ ] DPA (Data Processing Agreement) mit OpenRouter prüfen/abschließen
- [ ] Prüfung der Subprozessoren (welches LLM, wo gehostet)
- [ ] Ggf. On-Premise LLM oder EU-hosted Alternative evaluieren
- [ ] PII-Redaction vor LLM-Call implementieren
- [ ] Consent-Management für Transkript-Upload

---

## Stakeholder-Einbindung in Unternehmen/Konzern
Falls dieses System in einem mittleren bis großen Unternehmen produktiv eingesetzt werden soll:
| Stakeholder | Einbindung erforderlich? | Grund | Zeitpunkt |
|-------------|-------------------------|-------|-----------|
| **Datenschutzbeauftragter** | ✅ Ja | Personenbezogene Daten in Transkripten; Drittland-Transfer möglich | Während Konzeption |
| **Betriebsrat** | ⚠️ Ja, wenn... | ...Mitarbeiter-Transkripte verarbeitet werden → potenzielle Leistungsüberwachung | Während Konzeption |
| **Legal & Compliance** | ✅ Ja | Vertragsgestaltung mit OpenRouter; IP-Rechte an extrahierten Use Cases | Während Konzeption |
| **IT-Security** | ✅ Ja | API-Key-Management; Zugriffskontrolle; Penetration Testing | Während Konzeption |
| **Informationssicherheitsbeauftragter** | ✅ Ja | Klassifizierung der Daten; Risikobewertung | Während Konzeption |

**Für diesen Prototyp:** Nicht relevant, da synthetische Daten + lokaler Betrieb.

---

## IT-Security
### Implementierte Maßnahmen (MVP)
| Maßnahme | Status | Details |
|----------|--------|---------|
| API-Key nicht im Repo | ✅ Umgesetzt | `.env` in `.gitignore`; `.env.example` ohne Werte |
| Passwort-Hashing | ✅ Umgesetzt | bcrypt mit Salt |
| JWT-Authentifizierung | ✅ Umgesetzt | Signierte Tokens mit Expiry |
| RBAC | ✅ Umgesetzt | Rollen-Check auf API-Endpoints + Agent-Tools |
| Input-Validierung | ✅ Umgesetzt | Pydantic-Schemas für alle Inputs |
| SQL Injection Prevention | ✅ Umgesetzt | SQLAlchemy ORM (keine Raw Queries) |
| XSS Prevention | ✅ Umgesetzt | React escaped by default |
| CORS | ✅ Umgesetzt | Eingeschränkt auf Frontend-Origin |

### Nicht implementiert (Out of Scope MVP)
| Maßnahme | Grund für Ausschluss |
|----------|---------------------|
| HTTPS/TLS | Lokaler Betrieb; für Produktion: Reverse Proxy mit TLS |
| Rate Limiting | Kein öffentliches Exposure |
| CSRF Protection | JWT-basiert (kein Cookie-Auth) |
| Audit Logging | Nice-to-have; nicht MVP |
| Secrets Management (Vault etc.) | Overkill für lokalen Prototyp |
| Penetration Testing | Prototyp-Phase |
| 2FA/MFA | Über MVP hinaus |

---

## Guardrails für LLM
### Implementiert (MVP)
| Guardrail | Implementierung | Ziel | Status |
|------------|-----------------|------|--------|
| Output-Schema-Validierung | Pydantic-Modell für erwartete Struktur | Ungültiges JSON abfangen | ✅ Umgesetzt |
| Retry bei Parsing-Fehler | Max 2 Retries mit Hinweis im Prompt | Robustheit erhöhen | ✅ Umgesetzt |
| User-Content-Trennung | System-Prompt vs. User-Content klar getrennt | Prompt Injection erschweren | ✅ Umgesetzt |
| Token-Limit prüfen | Transkript-Länge vor Senden prüfen | Context-Overflow verhindern | 🚧 Teilweise — Dateigrößen-Limit (500 KB) im Frontend, aber kein echtes Token-Counting |
| Strukturiertes Logging | Jeder LLM-Call wird geloggt (Request-ID, Tokens, Latenz) | Nachvollziehbarkeit |🚧 Teilweise — Standard Python logger.info() mit Model + Message-Count, aber keine Request-ID, kein Token-Counting, keine Latenz |

### Nicht implementiert (Out of Scope MVP)
| Guardrail | Grund für Ausschluss |
|------------|---------------------|
| Content Moderation | Interne Business-Daten; kein User-Generated Public Content |
| Prompt Injection Detection | Aufwand vs. Risiko für internen Prototyp unverhältnismäßig |
| PII Redaction vor LLM-Call | Synthetische Daten; für Produktion erforderlich |
| Output-Content-Filter | Interne Daten; kein öffentliches Risiko |

---

## Zusammenfassung: Annahmen
| ID | Annahme | Auswirkung wenn falsch |
|----|---------|------------------------|
| A1 | Nur synthetische Testdaten | Datenschutz-Anforderungen steigen drastisch |
| A2 | Nur lokaler Betrieb | Security-Anforderungen steigen (HTTPS, Rate Limiting, WAF) |
| A3 | OpenRouter ist verfügbar und stabil | Fallback: Manuelles Use-Case-Anlegen funktioniert |
| A4 | Kein Multi-User gleichzeitig | Keine Concurrency-Konflikte zu behandeln |
| A5 | Transkripte sind <50k Tokens | Sonst: Chunking oder Ablehnung erforderlich |
| A6 | Kein Malicious User | Keine aktiven Angriffe auf das System |

---

## Checkliste vor Produktivbetrieb
Falls dieses System jemals produktiv eingesetzt werden soll:
- [ ] Echte TLS-Zertifikate einrichten
- [ ] Rate Limiting implementieren
- [ ] DPA mit OpenRouter abschließen
- [ ] PII-Redaction implementieren
- [ ] Audit-Logging aktivieren
- [ ] Penetration Test durchführen
- [ ] Datenschutzbeauftragten einbinden
- [ ] Betriebsrat informieren (falls relevant)
- [ ] Backup-Strategie definieren
- [ ] Incident-Response-Plan erstellen