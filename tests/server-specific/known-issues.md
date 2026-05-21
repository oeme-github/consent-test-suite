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

## KI-002: Custom SearchParameter – Unterstützung in Blaze

**Status:** Zu verifizieren
**Betrifft:** Blaze 0.28.x
**Entdeckt:** 2026-05-21
**Testfall:** TC-SEARCH-009 bis TC-SEARCH-012

### Beschreibung
Blaze unterstützt custom SearchParameter grundsätzlich via REST API.
Bei komplexen FHIRPath-Ausdrücken (verschachtelte Provisions) ist das
Verhalten nicht vollständig dokumentiert. Composite SearchParameter
(`mii-provision-provision-code-period`, `mii-provision-provision-code-type`)
werden möglicherweise nicht unterstützt.

### Erwartetes Verhalten
Laut FHIR R4 Spezifikation müssen custom SearchParameter via REST
registrier- und nutzbar sein.

### Workaround
Noch nicht bekannt. Tests TC-009 bis TC-012 markieren Blaze-Abweichungen
sobald erste Testläufe vorliegen.

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
