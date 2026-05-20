# Fixture-Katalog

**IG-Version:** MII Consent IG 1.0.7 (Simplifier)
**FHIR-Version:** R4

Alle Fixtures enthalten `"system": "https://www.medizininformatik-initiative.de/fhir/modul-consent/CodeSystem/Tags", "code": "test-fixture"`
im `meta.tag`, damit `setup.sh` sie zuverlässig bereinigen kann.

---

## Valide Fixtures (`valid/`)

| Datei | Szenario | patient | status | Hinweis |
|---|---|---|---|---|
| `consent-broad-erteilt.json` | Broad Consent vollständig erteilt | `test-patient-001` | `active` | Referenz-Fixture |
| `consent-broad-widerrufen.json` | Broad Consent widerrufen | `test-patient-001` | `inactive` | Gleicher Patient wie oben |
| `consent-spezifisch-studie-a.json` | Spezifische Einwilligung Studie A | `test-patient-002` | `active` | Abweichende `category` |
| `consent-expired.json` | Abgelaufener Consent | `test-patient-003` | `active` | `provision.period.end` in der Vergangenheit |

---

## Invalide Fixtures (`invalid/`)

Werden für Negativtests gegen `$validate` verwendet.
Diese Ressourcen werden **nicht** auf den Server geladen, sondern
nur für `$validate`-Aufrufe genutzt.

| Datei | Fehler | Erwartetes Ergebnis |
|---|---|---|
| `consent-missing-patient.json` | `patient`-Referenz fehlt | `OperationOutcome` mit `error` |
| `consent-unknown-policy.json` | Unbekannter Code in `policy.uri` | `OperationOutcome` mit `error` oder `warning` |
| `consent-invalid-status.json` | Ungültiger `status`-Wert | `OperationOutcome` mit `error` |

---

> ⚠️ TODO: Fixtures für folgende Szenarien noch erstellen:
> - Consent mit `actor`-Referenz (für actor-Suchtests)
> - Consent mit mehreren `provision`-Einträgen
> - Consent mit GICS-spezifischen Extensions
