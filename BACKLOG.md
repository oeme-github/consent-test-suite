# Backlog – consent-test-suite

## Letzter Stand

**Letzter Testlauf:** 2026-08-10 · HAPI 147/151 · Blaze 157/158 · Spark Search (vollständig) 137/158 (21 Failures: 9× KI-005 Custom-SP [TC-SEARCH-010/011/012/013/014/017], 12× KI-006 Stale Index [TC-UPDATE-001/002/003]) · CONF: HAPI 3/3 · Blaze 3/3 · Spark 1/3 (KI-007)
**Zuletzt abgeschlossen:** KI-006 vollständig durchleuchtet; Spark upstream gemeldet (#1319); MII #123 aktualisiert; docs/test-design-principles.md angelegt

### Abgeschlossen in dieser Session
- Upstream-Check: HAPI #8104, #8126 und Spark #1319 geprüft – alle weiterhin 0 Kommentare, kein Update nötig (docs/upstream-watch.md aktuell)
- Vollständiger Spark Search-Testlauf durchgeführt (72 Requests, 158 Assertions, 21 Failures – alle bereits bekannten Issues KI-005/KI-006 zuzuordnen, keine neuen Bugs)
- newman 6.2.2 auf der neuen Devbox nachinstalliert (fehlte trotz CLAUDE.md-Eintrag – vermutlich Devbox-Migrationslücke wie bei D06)
- F01 entschieden: bekannte Fehler laufen in CI als Warning. `test-hapi` in `.github/workflows/test.yml` bekam `continue-on-error: true` (Blaze/Spark hatten das bereits) + Eintrag in der Step-Summary-Tabelle für KI-003/KI-006; Step-Summary erklärt jetzt die Warning/Fail-Policy
- Blaze-Job-Kommentar korrigiert: KI-002 (behoben) durch KI-008 (aktuell) ersetzt
- D07: HAPI-Healthcheck nachgerüstet via `infrastructure/hapi.Dockerfile` (busybox-musl-Binary in distroless-Image), `docker-compose.yml` baut `hapi` jetzt lokal statt Vendor-Image direkt zu pullen; lokal verifiziert (alle vier Container "healthy")

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
| consent-test-suite_D06 | Docker-Healthchecks (`infrastructure/docker-compose.yml`) funktionierten nie: `hapi`/`spark` nutzten `curl`, das in beiden Images gar nicht existiert (`hapi` hat nicht mal eine Shell — rein JRE-basiertes Image, kein Exec-fähiges HTTP-Tool möglich). Beide Container meldeten dauerhaft "unhealthy", obwohl die Apps einwandfrei liefen (extern per `curl` bestätigt, `hapi`s eigene Access-Logs zeigten erfolgreiche Requests). Gefunden beim ersten echten Docker-Compose-Pilotlauf auf der neuen Devbox (`dev-notes/concepts/devbox-migration.md`), nicht Devbox-spezifisch — wäre unter WSL genauso aufgetreten, nur nie so genau nachgeprüft. **Gefixt:** `spark` (Alpine-Basis, hat `wget`) auf `wget --spider` umgestellt; `hapi`-Healthcheck komplett entfernt (technisch nicht möglich) statt notdürftig zu flicken, Kommentar im Compose-File erklärt warum. `blaze` unverändert (hatte `curl`, war nie betroffen). Nebenbei das veraltete `version: "3.8"`-Feld entfernt (Compose-Warnung). Alle vier Container nach Neustart verifiziert (`blaze`/`spark` "healthy", `hapi` läuft ohne falsches Warnsignal). | Niedrig | ✅ Erledigt |
| D07 | HAPI-Healthcheck doch nachrüsten (Folge-Entscheidung zu D06, "kein Healthcheck möglich" revidiert) | Niedrig | ✅ Erledigt (2026-08-10) — `infrastructure/hapi.Dockerfile` neu: wrappt `hapiproject/hapi:v7.4.0` (distroless, keine Shell) nur um ein statisch gelinktes `busybox:1.36.1-musl`-Binary (`COPY --from`), Anwendung/Version unverändert. **Stolperstein:** erster Versuch mit `busybox:1.36.1` (Default-Tag) schlug fehl – der ist dynamisch gegen glibc gelinkt (`GLIBC_2.38 not found`), da distroless-Image keine passende glibc mitbringt. `-musl`-Tag ist echt statisch, funktioniert. `docker-compose.yml`: `hapi`-Service baut jetzt lokal (`build:` statt `image:`) + `healthcheck` analog blaze/spark (`wget --spider`, `start_period: 120s`/`retries: 12` wegen HAPIs bekannt langsamem Start). Verifiziert: Container "healthy" nach ~10s Erstcheck, `GET /fhir/metadata` weiterhin HTTP 200. **Scope-Grenze:** nur lokales `docker-compose.yml` – GitHub-Actions-`services:`-Blöcke unterstützen kein `build:`, CI behält daher den bestehenden Host-seitigen Curl-Wait-Loop für HAPI unverändert. |

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
| F01 | Wie sollen bekannte Fehler in CI behandelt werden – Fail oder Warning? | ✅ Entschieden (2026-08-10): Warning – `continue-on-error` für alle drei Server-Jobs, siehe test-design-principles.md |
| F02 | Sollen TC-UPDATE-Tests mit `_refresh` serverseitig gefixt werden oder nur dokumentiert? | ✅ Entschieden: Bugs bleiben sichtbar (siehe test-design-principles.md) |
