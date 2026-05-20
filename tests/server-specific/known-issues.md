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

> ⚠️ TODO: Diese Datei wird gefüllt, sobald die ersten Testläufe
> Unterschiede identifizieren. Bitte bei jedem neuen Fund direkt
> hier dokumentieren – nicht nur im Issue-Tracker.

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
