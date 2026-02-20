# 3. Datenlage & Testdaten

## Ist-Situation
**Verfügbare echte Daten:** Keine. Der Auftraggeber (BadenCAMPUS) hat bestätigt, dass keine echten Workshop-Transkripte oder Use-Case-Daten zur Verfügung gestellt werden.

**Konsequenz:** Wir arbeiten ausschließlich mit synthetischen Testdaten. Alle Stammdaten (Industries, Companies, Users) werden über `backend/seed.py` in die Datenbank geschrieben.

---

## Synthetische Transkripte
Für die Demo wurden realistische, aber fiktive Workshop-Transkripte erstellt. Sie liegen in `backend/data/upload/`.

| Datei | Branche | Zweck |
|-------|---------|-------|
| stadtwerke-workshop-2026-01.txt | Energieversorgung | Haupt-Demo |
| maschinenbau-workshop-2026-02.txt | Maschinenbau | Demo |
| klinikum-workshop-2026-02.txt | Gesundheitswesen | Demo |
| test-kurz-ein-uc.txt | — | Edge Case: nur 1 Use Case |
| test-irrelevant-kein-uc.txt | — | Edge Case: kein Use Case erkennbar |
| test-prompt-injection.txt | — | Security-Test |
| test-prompt-injection_hard.txt | — | Security-Test (aggressiv) |

### Anforderungen an Transkripte
- Realistische Workshop-Struktur (Begrüßung → Problemdiskussion → Ideengenerierung → Abschluss)
- 3-5 erkennbare Use Cases pro Transkript
- Personen mit Rollen (z.B. „Dr. Maria Schmidt (Geschäftsführerin)")
- Deutsch, Plain Text (.txt), UTF-8, 2.000-5.000 Wörter

---

## Regeln für synthetische Daten
| Regel | Begründung |
|-------|------------|
| Keine echten Firmen-/Personennamen | DSGVO-Konformität + Haftung vermeiden |
| Realistische, aber fiktive Inhalte | Demo-Qualität ohne Compliance-Risiko |
| Deutsche Sprache, UTF-8 | Aufgabenstellung ist deutsch; Umlaute korrekt verarbeiten |
