# Backlog – consent-test-suite

## Letzter Stand

**Letzter Testlauf:** 2026-05-22 · HAPI 147/151 · Blaze 131/151 · Spark 131/151
**Zuletzt abgeschlossen:** analyze-tc.py CLI für Root-Cause-Analyse + CI-Pipeline für alle drei Server (HAPI, Blaze, Spark)

### Abgeschlossen in dieser Session
- (Onboarding – diese Datei wird neu angelegt)

---

## Offene Known Issues

| KI | Beschreibung | Betrifft | Status |
|----|-------------|---------|--------|
| KI-003 | Over-Matching bei Composite SP `provisionCodePeriod` | HAPI | Bestätigt |
| KI-006 | Stale Suchindex nach PUT (AND-Query TC-UPDATE-003) | HAPI, Blaze, Spark | Bestätigt |
| KI-002 | Nested FHIRPath in Custom SP | Blaze | Bestätigt |
| KI-005 | Custom SP nicht anwendbar | Spark | Bestätigt |

---

## Sprint / Milestone: CI-Stabilität & Testerweiterung

| ID | Aufgabe | Priorität | Status |
|----|---------|-----------|--------|
| S1-01 | CI-Pipeline: `continue-on-error` für Newman/HAPI evaluieren – wann wird Pipeline als Fehler markiert? | Hoch | 📋 Offen |
| S1-02 | TC-CONF-001 und TC-CONF-002 auf Spark ausführen und Ergebnis eintragen | Mittel | 📋 Offen |
| S1-03 | KI-006 (Stale Index / AND-Query) an HAPI und Blaze upstream melden | Hoch | 📋 Offen |
| S1-04 | KI-003 (HAPI Over-Matching) reproduzieren und upstream melden | Mittel | 📋 Offen |

---

## Entwicklung & Infrastruktur

| ID | Aufgabe | Priorität | Status |
|----|---------|-----------|--------|
| D01 | Firely/Spark: Setup-Skript und Fixture-Ladeweg prüfen (MII SP-Registrierung) | Mittel | 📋 Offen |
| D02 | `analyze-tc.py` in CI-Pipeline integrieren (Testergebnis-Auswertung automatisieren) | Niedrig | 📋 Offen |
| D03 | Newman-Collection in einzelne TC-Dateien aufteilen (aktuell alles in `search/collection.json`) | Niedrig | 📋 Offen |

---

## Offene GitHub Issues

| # | Titel | Priorität | Status |
|---|-------|-----------|--------|
| (keine) | — | — | — |

---

## Zurückgestellt

- **Firely Server**: Ursprünglich als dritter Server geplant, durch Spark ersetzt — Firely-spezifische Tests zurückgestellt

---

## Offene Fragen / Entscheidungen

| ID | Frage | Status |
|----|-------|--------|
| F01 | Wie sollen bekannte Fehler in CI behandelt werden – Fail oder Warning? | 📋 Offen |
| F02 | Sollen TC-UPDATE-Tests mit `_refresh` serverseitig gefixt werden oder nur dokumentiert? | 📋 Offen |
