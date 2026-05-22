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

**Status:** Bestätigt
**Betrifft:** Blaze 1.7.0
**Entdeckt:** 2026-05-21
**Testfall:** TC-SEARCH-010, TC-SEARCH-011, TC-SEARCH-012, TC-SEARCH-013, TC-SEARCH-014

### Beschreibung
Blaze akzeptiert die Registrierung aller MII Custom SearchParameter via REST (HTTP 201),
wendet sie bei der Suche jedoch nicht korrekt an, sobald der FHIRPath-Ausdruck
verschachtelte `provision`-Elemente adressiert.

Konkret: Blaze gibt bei TC-010 bis TC-012 **alle 5 Consents** zurück, unabhängig
vom Suchwert. Bei Composite-SPs (TC-013, TC-014) kommt es ebenfalls zu Over-Matching.

Einfache SearchParameter ohne Nested-Zugriff (TC-009: `policy.uri`) funktionieren korrekt.

Testergebnis Blaze 1.7.0: **65/73 ✅ — 8 Fehler in TC-010 bis TC-014**

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

## KI-006: Stale Suchindex nach PUT-Update – Blaze und Spark

**Status:** Bestätigt
**Betrifft:** Blaze 1.7.0, Spark FHIR (r4-latest)
**Entdeckt:** 2026-05-22
**Testfall:** TC-UPDATE-001, TC-UPDATE-002

### Beschreibung

Nach einem `PUT` auf einen bestehenden Consent (z.B. `provision.type` von `permit` → `deny`)
liefert eine anschließende Suche nach dem alten Wert (`mii-provision-provision-type=permit`)
weiterhin den aktualisierten Consent — der Suchindex wird nicht aktualisiert.

TC-UPDATE-001 testet das direkt nach dem PUT.
TC-UPDATE-002 testet mit `?_refresh=true` — auch das hilft bei beiden Servern nicht.

Beide Assertion-Fehler:
```
expected 1 to equal 0   ← alter permit-Wert trifft noch immer nach Update
```

HAPI FHIR v7.4.0 aktualisiert den Suchindex nach PUT korrekt (TC-UPDATE-001/002: ✅).

### Erwartetes Verhalten

Nach einem erfolgreichen PUT darf der Suchindex keine veralteten Werte mehr liefern.
`_refresh=true` sollte als expliziter Hinweis auf sofortige Reindizierung wirken.

### Workaround

Keiner bekannt. Für produktive Deployments auf Blaze oder Spark muss mit einem
verzögerten Suchindex nach Updates gerechnet werden.

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
