# CLAUDE.md – KI-Einstiegspunkt für dieses Repository

> Diese Datei ist der primäre Kontext für KI-gestützte Arbeit (Claude Code, etc.).
> Bitte vor jeder Aufgabe vollständig lesen.

---

## Projektkontext

Dieses Repository enthält die automatisierte Testumgebung für **FHIR Consent**
gemäß dem **MII Broad Consent Profil** (Medizininformatik-Initiative).

**Zwei Teams arbeiten gemeinsam:**
- **HL7germany Arbeitsgruppe Einwilligungsmanagement**
- **MII Task Force Consent Umsetzung**

**Problem, das wir lösen:** Fehler und nicht funktionierende Suchanfragen bei
FHIR Consent-Implementierungen werden zunehmend gemeldet. Die Testumgebung soll
einen definierten, reproduzierbaren Zustand und automatisierte Regressionstests
ermöglichen.

---

## Architekturentscheidungen (Kurzform)

| Entscheidung | Kurzbegründung | Details |
|---|---|---|
| Server-agnostische Tests | Drei Server im Einsatz (HAPI, Blaze, Firely) | [ADR-0001](docs/adr/0001-server-agnostic-tests.md) |
| Fixture-basiertes Setup | Reproduzierbarer Ausgangszustand | [ADR-0002](docs/adr/0002-fixture-strategy.md) |
| FHIR TestScript + Newman | HL7-Standard + CI-Fähigkeit | [ADR-0003](docs/adr/0003-test-tooling.md) |
| Docker Compose pro Server | Fixe Versionen, portabel | [ADR-0004](docs/adr/0004-infrastructure.md) |

---

## Zielserver

Tests laufen gegen alle drei Server. Die Basis-URL wird per Umgebungsvariable
gesetzt – **nie** hartcodiert.

| Server | Umgebungsvariable | Standard (lokal) |
|---|---|---|
| HAPI FHIR | `FHIR_BASE_HAPI` | `http://localhost:8080/fhir` |
| Blaze | `FHIR_BASE_BLAZE` | `http://localhost:8081/fhir` |
| Spark FHIR | `FHIR_BASE_SPARK` | `http://localhost:8082/fhir` |

---

## Verzeichnisstruktur

```
consent-test-suite/
├── CLAUDE.md                    ← Diese Datei
├── README.md                    ← Community-Einstiegspunkt
├── docs/
│   ├── architecture.md          ← Gesamtarchitektur
│   ├── getting-started.md       ← Setup-Guide
│   └── adr/                     ← Architecture Decision Records
├── fixtures/
│   ├── README.md                ← Fixture-Katalog
│   ├── valid/                   ← Valide Consent-Ressourcen
│   └── invalid/                 ← Invalide Ressourcen (für Negativtests)
├── tests/
│   ├── README.md                ← Testfall-Katalog
│   ├── conformance/             ← Validierung gegen IG-Profile
│   ├── search/                  ← Search-Parameter-Tests
│   └── server-specific/         ← Bekannte Serverunterschiede
├── infrastructure/
│   ├── docker-compose.yml       ← Alle drei Server
│   └── setup.sh                 ← Fixtures laden, Server initialisieren
└── .github/
    └── workflows/
        └── test.yml             ← CI/CD Pipeline
```

---

## Wie man einen neuen Test hinzufügt

1. **Fixture anlegen** (falls noch nicht vorhanden):
   `fixtures/valid/<szenario>.json` oder `fixtures/invalid/<szenario>.json`
2. **Testfall schreiben**:
   - Conformance-Tests: `tests/conformance/TC-CONF-XXX-<name>.json` (FHIR TestScript)
   - Search-Tests: `tests/search/TC-SEARCH-XXX-<name>.json`
3. **Testfall im Katalog dokumentieren**: `tests/README.md` ergänzen
4. **Bekannte Serverunterschiede** sofort in `tests/server-specific/known-issues.md` eintragen

---

## Bekannte Einschränkungen & Fallstricke

> ⚠️ TODO: Diese Sektion wird laufend ergänzt, sobald Serverunterschiede
> identifiziert werden. Siehe auch `tests/server-specific/known-issues.md`.

---

## Glossar

| Begriff | Bedeutung |
|---|---|
| **MII** | Medizininformatik-Initiative |
| **Broad Consent** | Übergreifendes Einwilligungsmodell der MII für Forschungsdaten |
| **FHIR Consent** | HL7 FHIR R4 Consent-Ressource |
| **IG** | Implementation Guide (z.B. auf Simplifier.net veröffentlicht) |
| **Fixture** | Vordefinierte FHIR-Ressource für Testzwecke |
| **Search Parameter** | FHIR-Suchparameter wie `patient`, `status`, `category` |
| **TC** | Test Case (Testfall-Kürzel) |
| **ADR** | Architecture Decision Record |

---

## Relevante externe Ressourcen

- MII Consent IG auf Simplifier: `https://simplifier.net/MedizininformatikInitiative-ModulConsent`
- HL7 FHIR R4 Consent: `https://hl7.org/fhir/R4/consent.html`
- HL7 FHIR TestScript: `https://hl7.org/fhir/R4/testscript.html`
