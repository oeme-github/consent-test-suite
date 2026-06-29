# Bekannte Serverunterschiede

Diese Datei dokumentiert bekannte Abweichungen zwischen HAPI, Blaze und Firely.
Sie ist Grundlage für testspezifische Anmerkungen im Testfall-Katalog.

**Format:**
```
## KI-NNN: Kurzbeschreibung
Status: Offen | Bestätigt | Behoben
Betrifft: Server + Version
Entdeckt: Datum, Issue-Link falls vorhanden
```

---

## KI-001: Custom SearchParameter – Reindexierung in HAPI

**Status:** Bekannt (Design)
**Betrifft:** HAPI FHIR v7.x
**Entdeckt:** 2026-05-21
**Testfall:** TC-SEARCH-009 bis TC-SEARCH-012

### Beschreibung
HAPI FHIR verarbeitet neu registrierte custom SearchParameter asynchron.
Ressourcen, die **vor** der SP-Registrierung geladen wurden, werden nicht
automatisch reindiziert.

### Erwartetes Verhalten
Da `setup.sh` SearchParameter **vor** den Fixtures lädt, sind neu geladene
Consents sofort korrekt indexiert. Kein zusätzlicher Schritt nötig.

### Workaround
Falls SearchParameter nach Fixtures geladen werden (z.B. manuell):
`POST /\$reindex` mit Body `{"resourceType":"Parameters","parameter":[{"name":"resourceType","valueCode":"Consent"}]}`

---

## KI-002: Custom SearchParameter – Nested FHIRPath-Ausdrücke in Blaze

**Status:** Bestätigt (Blaze 1.9.0 — kein Fortschritt gegenüber 1.7.0)
**Betrifft:** Blaze 1.7.0–1.9.0
**Entdeckt:** 2026-05-21
**Testfall:** TC-SEARCH-010, TC-SEARCH-011, TC-SEARCH-012, TC-SEARCH-013, TC-SEARCH-014

### Beschreibung
Blaze akzeptiert die Registrierung aller MII Custom SearchParameter via REST (HTTP 201),
wendet sie bei der Suche jedoch nicht korrekt an, sobald der FHIRPath-Ausdruck
verschachtelte `provision`-Elemente adressiert.

Konkret: Blaze gibt bei TC-010 bis TC-012 **alle 5 Consents** zurück, unabhängig
vom Suchwert. Bei Composite-SPs (TC-013, TC-014) kam es in Blaze 1.7.0 zusätzlich
zu einem `AbstractMethodError` wenn `mii-provision-provision-code-type` als
sekundäre (seek) Klause kombiniert wurde.

Einfache SearchParameter ohne Nested-Zugriff (TC-009: `policy.uri`) funktionieren korrekt.

Testergebnis Blaze 1.7.0: **65/73 ✅ — 8 Fehler in TC-010 bis TC-014**

### Testergebnis Blaze 1.9.0 (2026-06-18)
**131/151 ✅ — 20 Fehler in TC-010–014 und TC-UPDATE-001–003. Identisch zu 1.7.0.**

TC-010–012 (einfache nested-FHIRPath-SPs): weiter Over-Matching (5 statt 4 bzw. 2 Treffer).
TC-013–014 (Composite-SPs standalone): weiter Over-Matching (5 statt 2–3 Treffer).

**TC-SEARCH-017 (2026-06-18): Kombinierte Suche `patient=X&mii-provision-provision-code-type=...$deny`**
Blaze v1.8.0 behebt [#3642](https://github.com/samply/blaze/issues/3642) —
den `AbstractMethodError` wenn `mii-provision-provision-code-type` als sekundäre Klause mit einem
selektiveren Parameter (`patient`) kombiniert wird. TC-017 Sub-request 1 (`$permit`) **bestätigt den Fix**:
`patient=test-patient-001&mii-provision-provision-code-type=...3.19$permit` → 1 Treffer, kein Fehler ✅

TC-017 Sub-request 2 (`$deny`) **bestätigt KI-002 auch in kombinierter Abfrage**:
`patient=test-patient-001&mii-provision-provision-code-type=...3.19$deny` → `total: 1` (erwartet: 0).
Blaze ignoriert den Typ-Filter selbst wenn der Patienten-Filter korrekt angewendet wird.
Das Over-Matching ist unabhängig davon ob der Composite-SP als Scan- oder Seek-Klause ausgewertet wird.

### Erwartetes Verhalten
Nur Consents, deren `provision.provision`-Elemente dem Suchwert entsprechen,
sollen zurückgeliefert werden.

### Workaround
Keiner bekannt. Für produktive Blaze-Deployments müssen alternative
Suchstrategien (z.B. Client-seitiges Filtering) geprüft werden.

---

## KI-003: Composite SearchParameter – Over-Matching bei provisionCodePeriod in HAPI

**Status:** Bestätigt
**Betrifft:** HAPI FHIR v7.4.0
**Entdeckt:** 2026-05-21
**Testfall:** TC-SEARCH-013

### Beschreibung
Bei der Abfrage `mii-provision-provision-code-period=<code>$ge2054-01-01` liefert
HAPI einen Consent zurück, dessen BIOMAT-lagern-Provision bis `2053-06-01` läuft —
also **vor** dem gesuchten Datum.

Betroffener Consent: `mii-consent-mit-actor-001` (BIOMAT lagern endet 2053-06-01).
Abfrage erwartet Treffer nur mit Periode `ge2054-01-01`.

### Ursache (Hypothese)
HAPI verknüpft beim Composite-SearchParameter Code und Periode nicht streng auf
Ebene der einzelnen `provision`-Instanz. Es scheint, dass der Code aus einer
Nested-Provision und die Periode aus der übergeordneten Provision (`provision.period`)
kombiniert werden, anstatt beide aus derselben Provision-Instanz zu nehmen.

### Erwartetes Verhalten
Laut FHIR R4 Composite-SearchParameter-Spezifikation müssen beide Komponenten
(code + period) aus **derselben** Provision-Instanz stammen.
Korrekte Treffermenge: 2 Consents (erteilt + widerrufen, jeweils Ende 2054-01-15).

### Workaround
Kein serverseitiger Workaround bekannt. Der Test (TC-SEARCH-013) prüft
per `at.least(2)`, dass die erwarteten IDs vorhanden sind — die Über-Treffermenge
von HAPI wird toleriert und hier dokumentiert.

---

## KI-005: Spark FHIR – OperationOutcome im Search-Bundle und fehlende nested-SP-Filterung

**Status:** Bestätigt
**Betrifft:** Spark FHIR (sparkfhir/spark:r4-latest, Incendi)
**Entdeckt:** 2026-05-21
**Testfall:** TC-SEARCH-009 (⚠️), TC-SEARCH-010–014 (❌)

### Beschreibung

**Problem 1: OperationOutcome im Search-Bundle (TC-009)**
Spark fügt bei Suchanfragen einen `OperationOutcome`-Entry in das Ergebnis-Bundle ein.
Dieser Entry hat kein `policy`-Feld, was Assertions, die alle Entries prüfen, zum Fehlschlagen bringt.
Laut FHIR R4-Spezifikation dürfen Search-Bundles keine OperationOutcomes als reguläre Entries enthalten.
Workaround: Test-Assertions filtern nach `resourceType === 'Consent'`.

**Problem 2: Nested FHIRPath-SPs (TC-010–014)**
Identisches Verhalten wie Blaze (KI-002): Spark akzeptiert Custom-SearchParameter-Registrierung (HTTP 201),
filtert bei verschachtelten `provision`-Feldern aber nicht korrekt. Es werden alle 5 Consents
zurückgegeben, unabhängig vom Suchwert.

Testergebnis Spark r4-latest: **64/73 ✅ — 9 Fehler (1× TC-009, 8× TC-010–014)**

### Workaround
Keiner für die nested-SP-Filterung bekannt. TC-009-Assertion defensiv auf Consent-Only gefiltert.

---

## KI-004: Firely Server – Lizenzpflicht ab Version 5.x

**Status:** Bestätigt
**Betrifft:** Firely Server 5.9.x, 6.x
**Entdeckt:** 2026-05-21
**Testfall:** alle

### Beschreibung
Firely Server (Docker-Image `firely/server`) startet nicht ohne eine gültige
Lizenzdatei `/app/firelyserver-license.json`. Das gilt auch für Version 5.9.1.
Ohne Lizenz bricht der Startvorgang mit `VonkConfigurationException` ab.

Fehlermeldung:
```
License from 'firelyserver-license.json' is not valid.
Startup failed.
```

### Workaround
Eine kostenlose Evaluierungslizenz kann unter https://fire.ly/products/firely-server
beantragt werden. Die Lizenzdatei muss per Docker-Volume in den Container gemountet
werden:
```yaml
volumes:
  - ./infrastructure/firely-license.json:/app/firelyserver-license.json:ro
```
Die Datei `infrastructure/firely-license.json` ist in `.gitignore` eingetragen
(enthält persönliche Lizenzinformationen).

---

## KI-006: Stale Suchindex nach PUT-Update (AND-Query)

**Status:** Bestätigt
**Betrifft:** Blaze 1.7.0–1.9.0, Spark FHIR (r4-latest), HAPI FHIR v7.4.0 (AND-Query spezifisch)
**Entdeckt:** 2026-05-22
**Analysiert:** 2026-05-22
**Testfall:** TC-UPDATE-001, TC-UPDATE-002, TC-UPDATE-003
**MII Issue:** [#123](https://github.com/medizininformatik-initiative/kerndatensatzmodul-consent/issues/123)
**Hinweis Blaze v1.9.0:** [#3710](https://github.com/samply/blaze/issues/3710) behebt veraltete `_lastUpdated`-Werte nach No-op-Updates, aber **nicht** den allgemeinen Stale-Index nach inhaltlichen PUTs — KI-006 bleibt offen.

### Beschreibung

Nach einem `PUT` auf einen bestehenden Consent wird bei AND-Queries der Suchindex
nicht korrekt aktualisiert. Das Verhalten unterscheidet sich nach Server und Abfragetyp:

| Server | Einzelner param (TC-001/002) | AND-Query zwei params (TC-003) |
|---|:---:|:---:|
| HAPI v7.4.0 | ✅ korrekt | ❌ Stale Index |
| Blaze 1.7.0 | ❌ Stale Index | ❌ Stale Index |
| Spark r4-latest | ❌ Stale Index | ❌ Stale Index |

**TC-UPDATE-003** repliziert das Szenario aus Issue #123 direkt:
Suche mit `mii-provision-provision-code-type=...3.7$permit` **UND**
`mii-provision-provision-code-type=...3.8$permit` (gleicher Parameter zweimal = AND-Bedingung).
Nach PUT `.3.7 → deny` liefert HAPI weiterhin `total: 4` statt des erwarteten
sinkenden Werts (4→3→2→1→0).

`_refresh=true` (TC-UPDATE-002) wirkt bei keinem der drei Server.

### Ursache (HAPI v7.4.0)

**Single-Provision-Consents + Single-SP-Suche:** Funktioniert korrekt nach PUT.
TC-UPDATE-001 (je eine Provision pro Consent, Suche mit einem SP) besteht
konsistent in Newman-Läufen (26/26).

**Dual-Provision-Consents:** Schlägt bereits bei Single-SP-Suche fehl.
Sobald ein Consent **mehrere** Nested-Provisions hat (`.3.7=permit` und `.3.8=permit`),
und nur eine davon durch PUT geändert wird (`.3.7→deny`), bleibt der Suchindex stale —
unabhängig davon ob eine oder zwei SP-Parameter in der Suche verwendet werden.

Reproduzierbar via `scripts/analyze-tc.py --tc TC-UPDATE-003 --server hapi`:
Probe zeigt single-SP und AND-Query beide stale; auch `POST $reindex` behebt
das Problem nicht.

Der Fehler liegt **nicht** im Search-Result-Cache
(`reuse_cached_search_results_millis=0` wurde getestet, behebt das Problem nicht),
sondern im Index-Update-Pfad beim Composite-SP für Consents mit mehreren
Nested-Provisions.

Dieser Mechanismus trifft exakt das in Issue #123 beschriebene Praxisszenario:
Suche nach Consents mit gleichzeitigem `.3.7=permit` und `.3.8=permit` liefert
nach Widerruf von `.3.7` weiterhin alle vier ursprünglichen Consents.

### Erwartetes Verhalten

Nach einem erfolgreichen PUT darf der Suchindex keine veralteten Werte mehr liefern,
unabhängig davon ob ein oder mehrere gleichnamige Suchparameter übergeben werden.

### Workaround

**HAPI:** Keiner bekannt. `reuse_cached_search_results_millis=0` behebt das Problem nicht.
`$reindex` nach jedem PUT behebt das Problem für Dual-Provision-Consents ebenfalls nicht
(Analyse via `analyze-tc.py` bestätigt). Workaround für Produktivbetrieb unbekannt.

**Blaze / Spark:** Auch Einzel-SP-Suchen nach UPDATE sind betroffen, kein Workaround bekannt.

---

## KI-007: Spark FHIR – $validate-Operation nicht implementiert

**Status:** Bestätigt
**Betrifft:** Spark FHIR (sparkfhir/spark:r4-latest)
**Entdeckt:** 2026-06-29
**Testfall:** TC-CONF-001, TC-CONF-002

### Beschreibung
Spark gibt bei jeder Anfrage an `POST /Consent/$validate` HTTP 500 zurück:
```
OperationOutcome.issue: severity=error, diagnostics="NotImplementedException: The method or operation is not implemented."
```
Die `$validate`-Operation ist in Spark nicht implementiert. TC-CONF-001 und TC-CONF-002
schlagen daher beide fehl, unabhängig davon ob die Eingaberessource valide oder invalide ist.

### Erwartetes Verhalten
Laut FHIR R4 soll `POST /[Resource]/$validate` eine Ressource gegen das deklarierte Profil
prüfen und ein `OperationOutcome` mit Severity `error`/`warning`/`information` zurückliefern
(nicht HTTP 500).

### Workaround
Profile-Validierung nur über externe Tools (HL7 FHIR Validator, Touchstone) möglich.
Für CI wird `validate-fixtures` bereits offline mit dem HL7 Validator durchgeführt.

---

## Vorlage für neuen Eintrag

```markdown
## KI-001: <Kurzbeschreibung>

**Status:** Offen
**Betrifft:** Firely Server 5.x.x
**Entdeckt:** YYYY-MM-DD
**Testfall:** TC-SEARCH-XXX
**Issue:** https://github.com/.../issues/XXX

### Beschreibung
Was genau passiert? Welche Anfrage führt zu welchem unerwarteten Ergebnis?

### Erwartetes Verhalten
Was sollte laut FHIR R4 Spezifikation passieren?

### Workaround
Gibt es einen Workaround für betroffene Nutzer?
```
