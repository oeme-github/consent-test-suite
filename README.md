# FHIR Consent Testumgebung

Automatisierte Testumgebung für FHIR Consent gemäß
[MII Broad Consent Profil](https://simplifier.net/MedizininformatikInitiative-ModulConsent).

Entwickelt von **HL7germany Arbeitsgruppe Einwilligungsmanagement** und
**MII Task Force Consent Umsetzung**.

---

## Was dieses Repository enthält

- **Fixture-Bibliothek**: Kanonische FHIR Consent-Ressourcen für definierte Testszenarien
- **Testfall-Katalog**: Conformance-Tests und Search-Parameter-Tests
- **Infrastruktur**: Docker Compose für HAPI FHIR, Blaze und Firely Server
- **CI/CD**: Automatische Testausführung bei Änderungen

---

## Schnellstart

```bash
# 1. Server starten
docker compose -f infrastructure/docker-compose.yml up -d

# 2. Fixtures laden (SearchParameter + Patients + Consents)
./infrastructure/setup.sh hapi

# 3. Tests ausführen
./run-tests.sh hapi
```

Läuft auf **Linux** und **Windows WSL2**. Docker, Node.js und Newman werden benötigt.

Vollständige Anleitung inkl. WSL2-Setup: [docs/getting-started.md](docs/getting-started.md)

---

## Testabdeckung

| Kategorie | Beschreibung |
|---|---|
| **Conformance** | Validierung gegen MII Consent IG-Profile |
| **Search** | FHIR Search-Parameter (patient, status, category, date, actor, …) |
| **Server-spezifisch** | Dokumentierte Unterschiede zwischen HAPI, Blaze, Firely |

Vollständiger Testfall-Katalog: [tests/README.md](tests/README.md)

---

## Aktuelle Testergebnisse

| Server | Version | Ergebnis | Bekannte Fehler |
|---|---|---|---|
| HAPI FHIR | 7.4.0 | **147/151** | KI-006 (AND-Query) |
| Blaze | 1.7.0 | **131/151** | KI-002, KI-006 |
| Spark FHIR | r4-latest | **131/151** | KI-005, KI-006 |

### Bekannte Serverunterschiede (Kurzübersicht)

| ID | Beschreibung | Betrifft |
|---|---|---|
| KI-001 | Custom SP – asynchrone Reindizierung nach Registrierung | HAPI |
| KI-002 | Nested FHIRPath-SPs filtern nicht korrekt | Blaze |
| KI-003 | Composite SP provisionCodePeriod – Over-Matching | HAPI |
| KI-004 | Lizenzpflicht – Server ersetzt durch Spark | Firely |
| KI-005 | OperationOutcome im Search-Bundle, nested SP | Spark |
| KI-006 | Stale Suchindex nach PUT-Update (AND-Query auch HAPI) | HAPI, Blaze, Spark |

Details: [tests/server-specific/known-issues.md](tests/server-specific/known-issues.md)

---

## Beitragen

Fehler gefunden oder Testfall fehlt? Issues und Pull Requests sind willkommen.

Beim Hinzufügen neuer Testfälle bitte die Konventionen in
[tests/README.md](tests/README.md) beachten.

---

## Lizenz

Apache License 2.0 – siehe [LICENSE](LICENSE).

Copyright 2026 HL7germany Arbeitsgruppe Einwilligungsmanagement &
MII Task Force Consent Umsetzung
