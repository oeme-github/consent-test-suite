# Fixture-Katalog

**IG-Version:** MII Consent IG 2026.0.0 (kerndatensatzmodul-consent, master)
**FHIR-Version:** R4

Alle Fixtures enthalten `"system": "https://www.medizininformatik-initiative.de/fhir/modul-consent/CodeSystem/Tags", "code": "test-fixture"`
im `meta.tag`, damit `setup.sh` sie zuverlässig bereinigen kann.

---

## Valide Fixtures (`valid/`)

| Datei | Ressourcen-ID | Szenario | patient | status | Hinweis |
|---|---|---|---|---|---|
| `consent-broad-erteilt.json` | `mii-consent-broad-erteilt-001` | Broad Consent vollständig erteilt (MDAT + BIOMAT) | `test-patient-001` | `active` | Referenz-Fixture, abgeleitet von MII-Beispiel 1 |
| `consent-broad-widerrufen.json` | `mii-consent-broad-widerrufen-001` | Broad Consent widerrufen (alle Provisions deny) | `test-patient-002` | `inactive` | Widerruf-Szenario |
| `consent-spezifisch-studie-a.json` | `mii-consent-teilweise-erteilt-001` | Teileinwilligung (nur MDAT erlaubt, BIOMAT verweigert) | `test-patient-003` | `active` | Mixed permit/deny auf Provision-Ebene |
| `consent-expired.json` | `mii-consent-expired-001` | Historischer Consent mit abgelaufener Periode | `test-patient-004` | `active` | `provision.period.end` 2020, status absichtlich `active` (serverseitige Behandlung testen) |
| `consent-mit-actor.json` | `mii-consent-mit-actor-001` | Consent mit `provision.actor` (Forschungszentrum Berlin) | `test-patient-005` | `active` | IRCP-Rolle auf `Organization/forschungszentrum-berlin`, MDAT+BIOMAT permit, BIOMAT lagern/nutzen bis 2053 |

---

## Patient-Fixtures (`patients/`)

Werden von `setup.sh` vor den Consent-Fixtures geladen (`PUT /Patient/<id>`).
Ermöglichen `_include=Consent:patient`-Tests (TC-SEARCH-016).

| Datei | Ressourcen-ID | Wird referenziert von |
|---|---|---|
| `patient-001.json` | `test-patient-001` | consent-broad-erteilt-001 |
| `patient-002.json` | `test-patient-002` | consent-broad-widerrufen-001 |
| `patient-003.json` | `test-patient-003` | consent-teilweise-erteilt-001 |
| `patient-004.json` | `test-patient-004` | consent-expired-001 |
| `patient-005.json` | `test-patient-005` | consent-mit-actor-001 |

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
> - Consent mit mehreren `provision`-Einträgen
> - Consent mit GICS-spezifischen Extensions
