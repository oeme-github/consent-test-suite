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

### TC-SEARCH-002: Suche per status=active

**Datei:** `search/TC-SEARCH-002-search-by-status-active.json`
**Fixture:** `fixtures/valid/consent-broad-erteilt.json`, `fixtures/valid/consent-broad-widerrufen.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** Zwei Consents liegen vor (einer `active`, einer `inactive`).
Eine Suche `GET /Consent?status=active` soll nur den aktiven zurückliefern.

**Erwartetes Ergebnis:** Bundle mit `total: 1`.

---

### TC-SEARCH-003: Negativtest – unbekannter Patient

**Datei:** `search/TC-SEARCH-003-search-unknown-patient.json`
**Server:** HAPI 🔲 | Blaze 🔲 | Firely 🔲

**Szenario:** Suche nach einem Patient, für den kein Consent existiert.

**Erwartetes Ergebnis:** Bundle mit `total: 0`, HTTP 200
(kein 404 – das wäre ein Fehler).

---

> ⚠️ TODO: Weitere Testfälle ergänzen:
> - `category`-Suche
> - `date`-Bereichssuche
> - `actor`-Suche
> - `_include` / `_revinclude`
> - Kombinierte Parameter
