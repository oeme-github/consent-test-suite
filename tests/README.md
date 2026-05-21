# Testfall-Katalog

Alle Testfälle folgen dem Namensschema: `TC-<KATEGORIE>-<NUMMER>-<kurzname>`

| Kürzel | Kategorie |
|---|---|
| `TC-CONF` | Conformance / Validation |
| `TC-SEARCH` | Search Parameter |
| `TC-E2E` | End-to-End / Prozess |

**Serverstatus-Legende:** ✅ Pass · ❌ Fail · ⚠️ Abweichung (siehe Kommentar) · 🔲 Nicht getestet

---

## Conformance-Tests

### TC-CONF-001: Valider Broad Consent besteht $validate

**Datei:** `conformance/TC-CONF-001-validate-broad-consent.json`
**Fixture:** `fixtures/valid/consent-broad-erteilt.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** Ein valider MII Broad Consent wird per `$validate`-Operation
geprüft. Der Server soll kein `error`-Severity-Issue zurückliefern.

**Erwartetes Ergebnis:** `OperationOutcome` ohne Issue vom Typ `error`.

---

### TC-CONF-002: Consent ohne Pflichtfeld schlägt $validate fehl

**Datei:** `conformance/TC-CONF-002-validate-missing-patient.json`
**Fixture:** `fixtures/invalid/consent-missing-patient.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** Ein Consent ohne `patient`-Referenz wird per `$validate`
geprüft. Der Server soll einen Fehler zurückliefern.

**Erwartetes Ergebnis:** `OperationOutcome` mit mindestens einem Issue
vom Typ `error`.

---

## Search-Parameter-Tests

### TC-SEARCH-001: Suche per patient-Referenz

**Datei:** `search/TC-SEARCH-001-search-by-patient.json`
**Fixture:** `fixtures/valid/consent-broad-erteilt.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** Ein Consent liegt für Patient `test-patient-001` vor.
Eine Suche `GET /Consent?patient=test-patient-001` soll genau
diesen Consent zurückliefern.

**Erwartetes Ergebnis:** Bundle mit `total: 1`, ein Entry mit der
korrekten Consent-Ressource, HTTP 200.

---

### TC-SEARCH-002: Suche per status=active (patient-gefiltert)

**Datei:** `search/collection.json`
**Fixture:** `fixtures/valid/consent-broad-erteilt.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** Suche `GET /Consent?patient=Patient/test-patient-001&status=active`.
Patient 001 hat genau einen aktiven Consent (erteilt).

**Erwartetes Ergebnis:** Bundle mit `total: 1`, status=active.

---

### TC-SEARCH-003: Negativtest – unbekannter Patient

**Datei:** `search/collection.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** Suche nach einem Patient, für den kein Consent existiert.

**Erwartetes Ergebnis:** Bundle mit `total: 0`, HTTP 200
(kein 404 – das wäre ein Fehler).

---

### TC-SEARCH-004: Suche per category (LOINC 57016-8)

**Datei:** `search/collection.json`
**Fixtures:** alle 4 validen Fixtures
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** Suche `GET /Consent?category=http://loinc.org|57016-8`.
Alle Fixtures tragen diese Category.

**Erwartetes Ergebnis:** Bundle mit `total: 4`. Jeder Entry hat LOINC 57016-8 in `category`.

---

### TC-SEARCH-005: Datumsbereichssuche (date ge/le)

**Datei:** `search/collection.json`
**Fixtures:** consent-broad-erteilt (2024-01-15), consent-broad-widerrufen (2024-01-15), consent-spezifisch-studie-a (2023-11-01), consent-expired (2010-06-01)
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario A:** `GET /Consent?date=ge2023-01-01&date=le2024-12-31`
→ 3 Treffer (expired aus 2010 ausgeschlossen).

**Szenario B:** `GET /Consent?date=lt2020-01-01`
→ 1 Treffer (nur consent-expired mit dateTime 2010).

---

### TC-SEARCH-006: Suche per status=inactive

**Datei:** `search/collection.json`
**Fixture:** `fixtures/valid/consent-broad-widerrufen.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** Suche `GET /Consent?status=inactive`.
Nur der widerrufene Consent hat status=inactive.

**Erwartetes Ergebnis:** Bundle mit `total: 1`, status=inactive.

---

### TC-SEARCH-007: Kombinierte Suche (patient + status)

**Datei:** `search/collection.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario A:** `GET /Consent?patient=Patient/test-patient-002&status=inactive`
→ 1 Treffer (widerrufen).

**Szenario B:** `GET /Consent?status=active`
→ 3 Treffer (erteilt, teilweise, expired — alle haben status=active).

---

### TC-SEARCH-008: Paginierung (_count)

**Datei:** `search/collection.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** `GET /Consent?_count=2` bei 4 vorhandenen Consents.

**Erwartetes Ergebnis:** Maximal 2 Einträge im Bundle. Entweder `total > 2`
oder ein `link` mit `relation: next` signalisiert weitere Seiten.

---

> ⚠️ TODO: Weitere Testfälle ergänzen:
> - `actor`-Suche (benötigt Fixtures mit `provision.actor`)
> - `_include=Consent:patient` (benötigt geladene Patient-Ressourcen)
> - MII-spezifische SearchParameter: `provisionCode`, `provisionPeriod`, `policyUri`
