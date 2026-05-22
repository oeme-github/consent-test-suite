# Testfall-Katalog

Alle Testfälle folgen dem Namensschema: `TC-<KATEGORIE>-<NUMMER>-<kurzname>`

| Kürzel | Kategorie |
|---|---|
| `TC-CONF` | Conformance / Validation |
| `TC-SEARCH` | Search Parameter |
| `TC-UPDATE` | Update / Lifecycle |
| `TC-E2E` | End-to-End / Prozess |

**Serverstatus-Legende:** ✅ Pass · ❌ Fail · ⚠️ Abweichung (siehe known-issues.md) · 🔲 Nicht getestet

---

## Aktueller Teststatus

Letzter Lauf: **2026-05-22** · HAPI 125/125 ✅ · Blaze 109/125 · Spark 109/125

| TC | Beschreibung | HAPI | Blaze | Spark |
|---|---|:---:|:---:|:---:|
| TC-CONF-001 | Valider Broad Consent besteht $validate | ✅ | ✅ | 🔲 |
| TC-CONF-002 | Fehlender Patient schlägt $validate fehl | ✅ | ✅ | 🔲 |
| TC-SEARCH-001 | Suche per patient-Referenz | ✅ | ✅ | ✅ |
| TC-SEARCH-002 | Suche per status=active | ✅ | ✅ | ✅ |
| TC-SEARCH-003 | Negativtest – unbekannter Patient | ✅ | ✅ | ✅ |
| TC-SEARCH-004 | Suche per category (LOINC 57016-8) | ✅ | ✅ | ✅ |
| TC-SEARCH-005 | Datumsbereichssuche (date ge/le) | ✅ | ✅ | ✅ |
| TC-SEARCH-006 | Suche per status=inactive | ✅ | ✅ | ✅ |
| TC-SEARCH-007 | Kombinierte Suche (patient + status) | ✅ | ✅ | ✅ |
| TC-SEARCH-008 | Paginierung (_count) | ✅ | ❌ | ✅ |
| TC-SEARCH-009 | MII SP – policyUri | ✅ | ❌ | ⚠️ KI-005 |
| TC-SEARCH-010 | MII SP – provisionCode | ✅ | ❌ KI-002 | ❌ KI-005 |
| TC-SEARCH-011 | MII SP – provisionPeriod | ✅ | ❌ KI-002 | ❌ KI-005 |
| TC-SEARCH-012 | MII SP – provisionType | ✅ | ❌ KI-002 | ❌ KI-005 |
| TC-SEARCH-013 | MII Composite SP – provisionCodePeriod | ⚠️ KI-003 | ❌ KI-002 | ❌ KI-005 |
| TC-SEARCH-014 | MII Composite SP – provisionCodeType | ✅ | ❌ KI-002 | ❌ KI-005 |
| TC-SEARCH-015 | actor-Suche (provision.actor) | ✅ | ✅ | ✅ |
| TC-SEARCH-016 | _include=Consent:patient | ✅ | ✅ | ✅ |
| TC-UPDATE-001 | Search-Konsistenz nach PUT (permit→deny) | ✅ | ❌ KI-006 | ❌ KI-006 |
| TC-UPDATE-002 | Search-Konsistenz nach PUT (_refresh) | ✅ | ❌ KI-006 | ❌ KI-006 |

---

## Conformance-Tests

> **Hinweis:** Die Conformance-Tests liegen als FHIR TestScript-Ressourcen vor
> und sind **nicht** mit Newman ausführbar. Sie werden aktuell nicht durch
> `run-tests.sh` oder die CI-Pipeline ausgeführt. Für die Ausführung wird ein
> FHIR TestScript-Runner (z.B. Touchstone) oder ein eigenes Skript benötigt.
> Die `validate-fixtures`-CI-Stage prüft die Fixtures bereits offline mit dem
> HL7 FHIR Validator.

### TC-CONF-001: Valider Broad Consent besteht $validate

**Datei:** `conformance/TC-CONF-001-validate-broad-consent.json`
**Fixture:** `fixtures/valid/consent-broad-erteilt.json`
**Server:** HAPI ✅ | Blaze ✅ | Spark 🔲

**Szenario:** Ein valider MII Broad Consent wird per `$validate`-Operation
geprüft. Der Server soll kein `error`-Severity-Issue zurückliefern.

**Erwartetes Ergebnis:** `OperationOutcome` ohne Issue vom Typ `error`.

---

### TC-CONF-002: Consent ohne Pflichtfeld schlägt $validate fehl

**Datei:** `conformance/TC-CONF-002-validate-missing-patient.json`
**Fixture:** `fixtures/invalid/consent-missing-patient.json`
**Server:** HAPI ✅ | Blaze ✅ | Spark 🔲

**Szenario:** Ein Consent ohne `patient`-Referenz wird per `$validate`
geprüft. Der Server soll einen Fehler zurückliefern.

**Erwartetes Ergebnis:** `OperationOutcome` mit mindestens einem Issue
vom Typ `error`.

---

## Search-Parameter-Tests

### TC-SEARCH-001: Suche per patient-Referenz

**Datei:** `search/TC-SEARCH-001-search-by-patient.json`
**Fixture:** `fixtures/valid/consent-broad-erteilt.json`
**Server:** HAPI ✅ | Blaze ✅ | Spark ✅

**Szenario:** Ein Consent liegt für Patient `test-patient-001` vor.
Eine Suche `GET /Consent?patient=test-patient-001` soll genau
diesen Consent zurückliefern.

**Erwartetes Ergebnis:** Bundle mit `total: 1`, ein Entry mit der
korrekten Consent-Ressource, HTTP 200.

---

### TC-SEARCH-002: Suche per status=active (patient-gefiltert)

**Datei:** `search/collection.json`
**Fixture:** `fixtures/valid/consent-broad-erteilt.json`
**Server:** HAPI ✅ | Blaze ✅ | Spark ✅

**Szenario:** Suche `GET /Consent?patient=Patient/test-patient-001&status=active`.
Patient 001 hat genau einen aktiven Consent (erteilt).

**Erwartetes Ergebnis:** Bundle mit `total: 1`, status=active.

---

### TC-SEARCH-003: Negativtest – unbekannter Patient

**Datei:** `search/collection.json`
**Server:** HAPI ✅ | Blaze ✅ | Spark ✅

**Szenario:** Suche nach einem Patient, für den kein Consent existiert.

**Erwartetes Ergebnis:** Bundle mit `total: 0`, HTTP 200
(kein 404 – das wäre ein Fehler).

---

### TC-SEARCH-004: Suche per category (LOINC 57016-8)

**Datei:** `search/collection.json`
**Fixtures:** alle 4 validen Fixtures
**Server:** HAPI ✅ | Blaze ✅ | Spark ✅

**Szenario:** Suche `GET /Consent?category=http://loinc.org|57016-8`.
Alle Fixtures tragen diese Category.

**Erwartetes Ergebnis:** Bundle mit `total: 5`. Jeder Entry hat LOINC 57016-8 in `category`.

---

### TC-SEARCH-005: Datumsbereichssuche (date ge/le)

**Datei:** `search/collection.json`
**Fixtures:** consent-broad-erteilt (2024-01-15), consent-broad-widerrufen (2024-01-15), consent-spezifisch-studie-a (2023-11-01), consent-expired (2010-06-01), consent-mit-actor (2024-06-01)
**Server:** HAPI ✅ | Blaze ✅ | Spark ✅

**Szenario A:** `GET /Consent?date=ge2023-01-01&date=le2024-12-31`
→ 4 Treffer (expired aus 2010 ausgeschlossen).

**Szenario B:** `GET /Consent?date=lt2020-01-01`
→ 1 Treffer (nur consent-expired mit dateTime 2010).

---

### TC-SEARCH-006: Suche per status=inactive

**Datei:** `search/collection.json`
**Fixture:** `fixtures/valid/consent-broad-widerrufen.json`
**Server:** HAPI ✅ | Blaze ✅ | Spark ✅

**Szenario:** Suche `GET /Consent?status=inactive`.
Nur der widerrufene Consent hat status=inactive.

**Erwartetes Ergebnis:** Bundle mit `total: 1`, status=inactive.

---

### TC-SEARCH-007: Kombinierte Suche (patient + status)

**Datei:** `search/collection.json`
**Server:** HAPI ✅ | Blaze ✅ | Spark ✅

**Szenario A:** `GET /Consent?patient=Patient/test-patient-002&status=inactive`
→ 1 Treffer (widerrufen).

**Szenario B:** `GET /Consent?status=active`
→ 4 Treffer (erteilt, teilweise, expired, mit-actor — alle haben status=active).

---

### TC-SEARCH-008: Paginierung (_count)

**Datei:** `search/collection.json`
**Server:** HAPI ✅ | Blaze ❌ | Spark ✅

**Szenario:** `GET /Consent?_count=2` bei 5 vorhandenen Consents.

**Erwartetes Ergebnis:** Maximal 2 Einträge im Bundle. Entweder `total > 2`
oder ein `link` mit `relation: next` signalisiert weitere Seiten.

---

### TC-SEARCH-009: MII SearchParameter – policyUri

**Datei:** `search/collection.json`
**Fixtures:** alle 5 validen Fixtures
**Server:** HAPI ✅ | Blaze ❌ | Spark ⚠️ (KI-005: OperationOutcome im Bundle, Assertion gefiltert)

**Voraussetzung:** `SearchParameter/mii-sp-consent-policyuri` muss auf dem Server registriert sein (`setup.sh` erledigt das).

**Szenario:** `GET /Consent?mii-policy-uri=urn:oid:2.16.840.1.113883.3.1937.777.24.2.1791`
→ alle 5 Fixtures haben diese Policy-OID.

**Erwartetes Ergebnis:** Bundle mit `total: 5`.

---

### TC-SEARCH-010: MII SearchParameter – provisionCode

**Datei:** `search/collection.json`
**Server:** HAPI ✅ | Blaze ❌ | Spark ❌

**Voraussetzung:** `SearchParameter/mii-sp-consent-provisioncode` registriert.

**Szenario:** `GET /Consent?mii-provision-provision-code=urn:oid:...|...3.19` (BIOMAT erheben)
→ erteilt, widerrufen, teilweise und mit-actor haben BIOMAT-erheben-Provision; expired nicht.

**Erwartetes Ergebnis:** Bundle mit `total: 4`. `mii-consent-expired-001` ist nicht enthalten.

---

### TC-SEARCH-011: MII SearchParameter – provisionPeriod

**Datei:** `search/collection.json`
**Server:** HAPI ✅ | Blaze ❌ | Spark ❌

**Voraussetzung:** `SearchParameter/mii-sp-consent-provisionperiod` registriert.

**Szenario:** `GET /Consent?mii-provision-provision-period=ge2030-01-01`
→ erteilt, widerrufen, teilweise und mit-actor haben Langzeit-Provisions bis 2053/2054; expired läuft 2020 ab.

**Erwartetes Ergebnis:** Bundle mit `total: 4`. `mii-consent-expired-001` ist nicht enthalten.

---

### TC-SEARCH-012: MII SearchParameter – provisionType

**Datei:** `search/collection.json`
**Server:** HAPI ✅ | Blaze ❌ | Spark ❌

**Voraussetzung:** `SearchParameter/mii-sp-consent-provisiontype` registriert.

**Szenario:** `GET /Consent?mii-provision-provision-type=deny`
→ widerrufen (alle Provisions deny) und teilweise (BIOMAT-Provisions deny) haben nested deny-Provisions;
erteilt und expired haben ausschließlich permit-Provisions.

**Erwartetes Ergebnis:** Bundle mit `total: 2` (widerrufen + teilweise).

---

### TC-SEARCH-013: MII Composite SearchParameter – provisionCodePeriod

**Datei:** `search/collection.json`
**Fixtures:** consent-broad-erteilt, consent-broad-widerrufen
**Server:** HAPI ⚠️ (KI-003: Over-Matching) | Blaze ❌ (KI-002) | Spark ❌ (KI-005)

**Voraussetzung:** `SearchParameter/mii-sp-consent-provisioncodeperiod` registriert.

**Szenario:** `GET /Consent?mii-provision-provision-code-period=urn:oid:2.16.840.1.113883.3.1937.777.24.5.3|2.16.840.1.113883.3.1937.777.24.5.3.20$ge2054-01-01`
→ BIOMAT lagern (`.20`) mit Periode bis mindestens 2054-01-01:
- erteilt: endet 2054-01-15 ✓
- widerrufen: endet 2054-01-15 ✓
- teilweise: endet 2053-11-01 (vor 2054) ✗
- expired: kein BIOMAT ✗

**Erwartetes Ergebnis:** Bundle mit `total: 2` (erteilt + widerrufen).

---

### TC-SEARCH-014: MII Composite SearchParameter – provisionCodeType

**Datei:** `search/collection.json`
**Fixtures:** consent-broad-widerrufen, consent-spezifisch-studie-a
**Server:** HAPI ✅ | Blaze ❌ | Spark ❌

**Voraussetzung:** `SearchParameter/mii-sp-consent-provisioncodetype` registriert.

**Szenario:** `GET /Consent?mii-provision-provision-code-type=urn:oid:2.16.840.1.113883.3.1937.777.24.5.3|2.16.840.1.113883.3.1937.777.24.5.3.19$deny`
→ BIOMAT erheben (`.19`) mit type=deny:
- erteilt: BIOMAT erheben ist permit ✗
- widerrufen: BIOMAT erheben ist deny ✓
- teilweise: BIOMAT erheben ist deny ✓
- expired: kein BIOMAT ✗

**Erwartetes Ergebnis:** Bundle mit `total: 2` (widerrufen + teilweise).

---

### TC-SEARCH-015: actor-Suche (provision.actor)

**Datei:** `search/collection.json`
**Fixture:** `fixtures/valid/consent-mit-actor.json`
**Server:** HAPI ✅ | Blaze ✅ | Spark ✅

**Szenario A:** `GET /Consent?actor=Organization/forschungszentrum-berlin`
→ Nur `mii-consent-mit-actor-001` hat diesen Actor in `provision.actor`.

**Erwartetes Ergebnis:** Bundle mit `total: 1`, ID ist `mii-consent-mit-actor-001`.

**Szenario B (Negativtest):** `GET /Consent?actor=Organization/unbekannt-999`
→ Kein Consent hat diesen Actor.

**Erwartetes Ergebnis:** Bundle mit `total: 0`, HTTP 200.

---

### TC-SEARCH-016: _include=Consent:patient

**Datei:** `search/collection.json`
**Fixtures:** `fixtures/patients/patient-001.json` + `fixtures/valid/consent-broad-erteilt.json`
**Server:** HAPI ✅ | Blaze ✅ | Spark ✅

**Szenario:** `GET /Consent?patient=Patient/test-patient-001&_include=Consent:patient`
→ Der Server soll den Consent und den referenzierten Patienten zurückliefern.

**Erwartetes Ergebnis:** Bundle mit Einträgen für `resourceType=Consent`
und `resourceType=Patient` (id=`test-patient-001`).

---

## Update / Lifecycle-Tests

> Diese Tests prüfen, ob der Suchindex nach einer PUT-Aktualisierung korrekt
> aktualisiert wird. Hintergrund: Issue #123 im MII Consent-Repository zeigt,
> dass HAPI und SMILE nach einem PUT noch veraltete Indexdaten liefern können.
> Die Tests sind self-contained: Sie erstellen und löschen ihren Consent selbst.

### TC-UPDATE-001: Search-Konsistenz nach PUT (permit → deny)

**Datei:** `search/collection.json`
**Server:** HAPI ✅ | Blaze ❌ (KI-006) | Spark ❌ (KI-006)
**MII Issue:** [#123](https://github.com/medizininformatik-initiative/kerndatensatzmodul-consent/issues/123)

**Szenario:**
1. 4 Consents (`mii-consent-update-test-001` bis `-004`) mit `.3.7 = permit` per PUT anlegen.
2. Suche `GET /Consent?patient=...update-001&mii-provision-provision-code-type=...|...3.7$permit` → `total: 4` (Vorbedingung).
3. Consents werden einzeln auf `deny` gesetzt. Nach jedem PUT wird die Suche wiederholt.

**Erwartete Treffermenge:** 4 → 3 → 2 → 1 → 0 (schrittweise Abnahme nach jedem Update).

**Befund:** HAPI aktualisiert den Suchindex nach jedem PUT sofort korrekt (125/125 ✅).
Blaze und Spark liefern nach dem Update weiterhin den alten Wert (Stale Index) → KI-006.

---

### TC-UPDATE-002: Search-Konsistenz nach PUT mit _refresh

**Datei:** `search/collection.json`
**Server:** HAPI ✅ | Blaze ❌ (KI-006) | Spark ❌ (KI-006)
**MII Issue:** [#123](https://github.com/medizininformatik-initiative/kerndatensatzmodul-consent/issues/123)

**Szenario:** Identisch zu TC-UPDATE-001, jedoch wird `_refresh=true` an jede Assert-Suchanfrage angehängt.

**Erwartete Treffermenge:** 4 → 3 → 2 → 1 → 0 (identisch zu TC-UPDATE-001, mit explizitem Refresh-Hint).

**Befund:** Weder Blaze noch Spark aktualisieren den Suchindex durch `_refresh=true` → KI-006.
