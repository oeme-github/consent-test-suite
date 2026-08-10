# Gesamtarchitektur

## Überblick

Die Testumgebung validiert FHIR Consent-Implementierungen gemäß dem MII Broad Consent Profil
gegen drei unterschiedliche FHIR-Server. Der Ansatz ist bewusst server-agnostisch: ein Test,
der auf HAPI läuft, muss auch auf Blaze und Firely laufen – mit identischem Ergebnis.

## Komponentendiagramm

```
┌──────────────────────────────────────────────────────────────┐
│                  CI/CD Pipeline (GitHub Actions)              │
│                                                              │
│   run-tests.sh                                               │
│       ├── newman (Search-Tests)                              │
│       └── FHIR TestScript-Runner (Conformance-Tests)         │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTP
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │ HAPI FHIR  │  │   Blaze    │  │   Firely   │
    │  v7.4.0    │  │  v0.28.1   │  │   v5.9.0   │
    │ :8080/fhir │  │ :8081/fhir │  │ :8082/fhir │
    └────────────┘  └────────────┘  └────────────┘
           ▲                ▲                ▲
           └────────────────┼────────────────┘
                            │
                      setup.sh
                   (Fixtures laden)
                            │
                    ┌───────────────┐
                    │  fixtures/    │
                    │  valid/*.json │
                    └───────────────┘
```

## Verzeichnisse und ihre Rolle

| Verzeichnis | Inhalt | Zweck |
|---|---|---|
| `fixtures/valid/` | Valide FHIR Consent-Ressourcen | Werden per `setup.sh` auf alle Server geladen |
| `fixtures/invalid/` | Invalide FHIR Consent-Ressourcen | Nur für `$validate`-Negativtests, nie auf Server geladen |
| `tests/conformance/` | FHIR TestScript-Ressourcen | Validierung gegen IG-Profile via `$validate` |
| `tests/search/` | Postman/Newman Collections | FHIR Search-Parameter-Tests |
| `tests/server-specific/` | Markdown-Dokumentation | Bekannte Serverunterschiede |
| `infrastructure/` | Docker Compose + setup.sh | Testumgebung starten und initialisieren |

## Fixture-Strategie

Fixtures sind kanonische FHIR-Ressourcen, die einen definierten, reproduzierbaren
Ausgangszustand sicherstellen. Alle Fixtures tragen das Meta-Tag:

```json
{
  "system": "https://www.medizininformatik-initiative.de/fhir/modul-consent/CodeSystem/Tags",
  "code": "test-fixture"
}
```

Dieses Tag ermöglicht `setup.sh`, genau diese Ressourcen selektiv zu löschen und neu zu laden,
ohne andere Daten auf dem Server zu berühren.

`setup.sh` führt bei jedem Lauf aus:
1. Warten bis Server bereit (Health Check gegen `/metadata`)
2. Alle Ressourcen mit Tag `test-fixture` löschen
3. Alle Fixtures aus `fixtures/valid/` neu laden

## Test-Tooling

### Conformance-Tests (FHIR TestScript)

- Format: HL7 FHIR R4 TestScript-Ressource (JSON)
- Dateiname: `tests/conformance/TC-CONF-XXX-<kurzname>.json`
- Testen die `$validate`-Operation gegen IG-Profile
- Können mit beliebigem FHIR TestScript-Runner ausgeführt werden

### Search-Tests (Newman/Postman)

- Format: Postman Collection v2.1.0 (JSON)
- Einzelne Testfälle: `tests/search/TC-SEARCH-XXX-<kurzname>.json`
- Master-Collection: `tests/search/collection.json` (bündelt alle Search-Tests)
- Ausführung: `newman run tests/search/collection.json --env-var "baseUrl=<url>"`
- Umgebungsvariable `{{baseUrl}}` wird zur Laufzeit gesetzt – nie hartcodiert

## Server-Konfiguration

| Server | Docker Image | Port (Host) | Port (Container) | Besonderheiten |
|---|---|---|---|---|
| HAPI FHIR | `hapiproject/hapi:v7.4.0` | 8080 | 8080 | Validation aktiviert |
| Blaze | `samply/blaze:0.28.1` | 8081 | 8080 | `BASE_URL` muss gesetzt werden |
| Firely Server | `firely/server:5.9.0` | 8082 | 4080 | Community Edition ausreichend |

Versionen sind explizit fixiert. Upgrades erfordern einen eigenen PR mit vollständigem Testlauf.

## Umgebungsvariablen

| Variable | Standard | Verwendung |
|---|---|---|
| `FHIR_BASE_HAPI` | `http://localhost:8080/fhir` | setup.sh, run-tests.sh |
| `FHIR_BASE_BLAZE` | `http://localhost:8081/fhir` | setup.sh, run-tests.sh |
| `FHIR_BASE_SPARK` | `http://localhost:8082/fhir` | setup.sh, run-tests.sh |

Basis-URLs werden **immer** per Umgebungsvariable übergeben, nie hartcodiert.

## CI/CD-Pipeline

Der GitHub Actions Workflow (`.github/workflows/test.yml`) führt folgende Schritte aus:

1. Docker Compose starten (`docker compose up -d`)
2. Auf Health Checks aller drei Server warten
3. `setup.sh` ausführen (Fixtures laden)
4. `run-tests.sh` ausführen (alle Tests, alle Server)
5. JUnit-XML-Ergebnisse als Build-Artefakte sichern

## Erweiterung um neue Tests

Konventionen siehe `tests/README.md`. Kurzform:
1. Fixture anlegen falls nötig (`fixtures/valid/` oder `fixtures/invalid/`)
2. Testdatei schreiben (`tests/conformance/` oder `tests/search/`)
3. Testfall in `tests/README.md` dokumentieren
4. Serverunterschiede in `tests/server-specific/known-issues.md` notieren

## Erweiterung um einen neuen Server

1. Service in `infrastructure/docker-compose.yml` ergänzen (explizite Version)
2. Neue Umgebungsvariable in `CLAUDE.md` und `infrastructure/setup.sh` aufnehmen
3. `run-tests.sh` um den neuen Server erweitern
4. Alle bestehenden Tests gegen den neuen Server ausführen und Ergebnisse dokumentieren
