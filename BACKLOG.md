# Backlog – consent-test-suite

## Letzter Stand

**Letzter Testlauf:** 2026-06-30 · HAPI 147/151 · Blaze 157/158 · Spark: TC-UPDATE-001/002/003 alle ❌ (12 Failures, Stale Index auch bei Single-Provision) · CONF: HAPI 3/3 · Blaze 3/3 · Spark 1/3 (KI-007)
**Zuletzt abgeschlossen:** D01 + Blaze-Nachtest – SP-Bundle-Mount: 157/158 Assertions ✅; 1 Failure: TC-SEARCH-013 (Composite SP – Blaze implementiert `type: composite` nicht)

### Abgeschlossen in dieser Session
- (Onboarding – diese Datei wird neu angelegt)

---

## Offene Known Issues

| KI | Beschreibung | Betrifft | Status |
|----|-------------|---------|--------|
| KI-003 | Over-Matching bei Composite SP `provisionCodePeriod` | HAPI | Bestätigt |
| KI-006 | Stale Suchindex nach PUT (Dual-Provision, AND-Query) | HAPI, Spark | Bestätigt; Blaze 1.9.0 behoben (2026-06-30) |
| KI-002 | Nested FHIRPath in Custom SP | Blaze | ✅ Kein Bug – Setup-Fehler behoben (SP-Bundle-Mount) |
| KI-008 | Composite SearchParameter (`type: composite`) nicht implementiert | Blaze | Bestätigt (2026-06-30) – TC-SEARCH-013 schlägt fehl |
| KI-005 | Custom SP nicht anwendbar | Spark | Bestätigt |
| KI-007 | $validate nicht implementiert | Spark | Bestätigt (2026-06-29) |

---

## Sprint / Milestone: CI-Stabilität & Testerweiterung

| ID | Aufgabe | Priorität | Status |
|----|---------|-----------|--------|
| S1-01 | CI-Pipeline: `continue-on-error` für Newman/HAPI evaluieren – wann wird Pipeline als Fehler markiert? | Hoch | ✅ Erledigt |
| S1-02 | TC-CONF-001 und TC-CONF-002 auf Spark ausführen und Ergebnis eintragen | Mittel | ✅ Erledigt (Spark ❌ KI-007: $validate HTTP 500 NotImplementedException; Newman-Collection erstellt) |
| S1-03 | KI-006 (Stale Index / AND-Query) an HAPI und Blaze upstream melden | Hoch | ✅ Erledigt (MII #123 kommentiert; HAPI hapifhir/hapi-fhir#8104; Blaze samply/blaze#3716 für KI-002) |
| S1-04 | KI-003 (HAPI Over-Matching) reproduzieren und upstream melden | Mittel | ✅ Erledigt (hapifhir/hapi-fhir#8126, 2026-06-29) |

---

## Entwicklung & Infrastruktur

| ID | Aufgabe | Priorität | Status |
|----|---------|-----------|--------|
| D01 | Blaze/Spark: SP-Registrierung prüfen (MII SP-Bundle) | Mittel | ✅ Erledigt für Blaze (SP-Bundle-Mount); Spark: KI-005 (Custom SP nicht unterstützt) bleibt |
| D02 | `analyze-tc.py` in CI-Pipeline integrieren (Testergebnis-Auswertung automatisieren) | Niedrig | 📋 Offen |
| D03 | Newman-Collection in einzelne TC-Dateien aufteilen (aktuell alles in `search/collection.json`) | Niedrig | 📋 Offen |
| D04 | MII-Testdaten-Repo evaluieren: `github.com/medizininformatik-initiative/mii-testdata/releases` – Releases sichten, prüfen ob offizielle Testdaten unsere Fixtures ersetzen oder ergänzen können | Mittel | ✅ Erledigt (Ergänzung, kein Ersatz – alle 10 Consents sind Volleinwilligungen ohne gezielte deny-Szenarien) |
| D05 | Blaze auf v1.9.0 aktualisieren (war v1.7.0 in `docker-compose.yml` und CI) – Changelog geprüft: #3642 (v1.8.0) behebt Composite-SP-Fehler mit `mii-provision-provision-code-type`; KI-002 (nested FHIRPath) und KI-006 (Stale Index) noch offen | Mittel | ✅ Erledigt (Update auf v1.9.0, Nachtest ausstehend) |

---

## Offene GitHub Issues

| # | Titel | Repo | Status |
|---|-------|------|--------|
| [#8104](https://github.com/hapifhir/hapi-fhir/issues/8104) | KI-006: Stale Suchindex nach PUT (AND-Query) | hapifhir/hapi-fhir | 0 Kommentare, offen |
| [#8126](https://github.com/hapifhir/hapi-fhir/issues/8126) | KI-003: Composite SP Over-Matching provisionCodePeriod | hapifhir/hapi-fhir | 0 Kommentare, offen (2026-06-29) |
| [#3716](https://github.com/samply/blaze/issues/3716) | KI-002: Nested FHIRPath in Custom SP | samply/blaze | ✅ Geschlossen (2026-06-30) – Setup-Fehler, kein Blaze-Bug |
| [#1319](https://github.com/FirelyTeam/spark/issues/1319) | KI-006: Stale Suchindex nach PUT (auch Single-Provision) | FirelyTeam/spark | Gemeldet (2026-06-30) |

---

## Zurückgestellt

- **Firely Server**: Ursprünglich als dritter Server geplant, durch Spark ersetzt — Firely-spezifische Tests zurückgestellt

---

## Offene Fragen / Entscheidungen

| ID | Frage | Status |
|----|-------|--------|
| F01 | Wie sollen bekannte Fehler in CI behandelt werden – Fail oder Warning? | 📋 Offen |
| F02 | Sollen TC-UPDATE-Tests mit `_refresh` serverseitig gefixt werden oder nur dokumentiert? | 📋 Offen |
