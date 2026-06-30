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

**Status:** ✅ Behoben (2026-06-30) — war kein Blaze-Bug, sondern Setup-Fehler
**Betrifft:** Blaze 1.7.0–1.9.0
**Entdeckt:** 2026-05-21
**Behoben:** 2026-06-30 — [samply/blaze#3716](https://github.com/samply/blaze/issues/3716) (geschlossen)
**Testfall:** TC-SEARCH-010, TC-SEARCH-011, TC-SEARCH-012

### Ursache
Blaze ignoriert SearchParameter-Ressourcen, die per REST (PUT/POST) registriert werden.
Custom SPs müssen beim Start über eine gemountete Bundle-Datei via `DB_SEARCH_PARAM_BUNDLE`
registriert werden. Unser `setup.sh` verwendete REST-POST — daher schienen die SPs
nicht zu wirken (Over-Matching).

### Fix
`infrastructure/blaze-sp-bundle.json` angelegt (FHIR Bundle mit allen 6 MII SPs);
`docker-compose.yml`: `DB_SEARCH_PARAM_BUNDLE: /app/blaze-sp-bundle.json` + Volume-Mount;
`setup.sh`: `load_searchparameters()` wird für Blaze übersprungen.

### Testergebnis nach Fix (2026-06-30, Blaze 1.9.0)
**157/158 Assertions ✅** — TC-010, 011, 012 bestehen korrekt.
Einzig TC-SEARCH-013 (Composite SP) schlägt fehl → siehe KI-008.

---

## KI-003: Composite SearchParameter – Over-Matching bei provisionCodePeriod in HAPI

**Status:** Bestätigt, upstream gemeldet
**Betrifft:** HAPI FHIR v7.4.0
**Entdeckt:** 2026-05-21
**Gemeldet:** 2026-06-29 — [hapifhir/hapi-fhir#8126](https://github.com/hapifhir/hapi-fhir/issues/8126)
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

## KI-008: Composite SearchParameter (`type: composite`) in Blaze nicht implementiert

**Status:** Bestätigt
**Betrifft:** Blaze 1.9.0
**Entdeckt:** 2026-06-30
**Testfall:** TC-SEARCH-013

### Beschreibung
Blaze implementiert SearchParameter vom Typ `composite` nicht. Beim Start wird geloggt:

```
WARN [blaze.db.impl.search-param.composite:67] - Skip creating search parameter
  `https://www.medizininformatik-initiative.de/fhir/modul-consent/SearchParameter/mii-sp-consent-provisioncodeperiod`
  of type `composite` because it is not implemented.
```

TC-SEARCH-013 (`mii-provision-provision-code-period=...3.19$ge2054-01-01`) schlägt daher fehl:
Blaze gibt alle 5 Consents zurück statt der erwarteten 2 (kein Filter wirksam).

Betroffen ist `mii-sp-consent-provisioncodeperiod` — der einzige Composite-SP im MII-Bundle.
Alle anderen MII Custom SPs (token, date, string) funktionieren korrekt nach SP-Bundle-Mount.

### Erwartetes Verhalten
Composite SPs sollen beide Komponenten (Code + Periode) innerhalb derselben
`provision`-Instanz prüfen.

### Workaround
Keiner serverseitig. Clients müssen Code- und Periodenfilter getrennt übergeben
und das Ergebnis client-seitig auf Provision-Ebene filtern.

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
