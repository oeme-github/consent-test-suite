# ADR-0001: Server-agnostische Tests

## Status
Akzeptiert

## Kontext

Die Testumgebung soll gegen drei FHIR-Server validieren:
**HAPI FHIR**, **Blaze** und **Firely Server**. Alle drei sind in
produktiven Umgebungen der MII im Einsatz.

Serverspezifische Tests würden bedeuten, dass jeder Testfall dreifach
gepflegt werden muss. Gleichzeitig gibt es reale Unterschiede zwischen
den Servern, die sichtbar gemacht werden müssen.

## Entscheidung

Alle Tests verwenden eine **abstrakte Basis-URL**, die per
Umgebungsvariable (`FHIR_BASE_URL`) zur Laufzeit gesetzt wird.

```bash
# Beispiel
FHIR_BASE_URL=http://localhost:8080/fhir ./run-tests.sh
```

Die CI-Pipeline führt die komplette Test-Suite sequenziell gegen
alle drei Server aus und erzeugt einen vergleichenden Report.

Unterschiede zwischen Servern werden **nicht** als Fehler im Test
versteckt, sondern **explizit in `tests/server-specific/known-issues.md`
dokumentiert**.

## Konsequenzen

**Positiv:**
- Ein Testfall deckt alle drei Server ab
- Serverunterschiede werden systematisch sichtbar und dokumentiert
- Neue Server können einfach ergänzt werden

**Negativ / Einschränkungen:**
- Serverspezifische Features (z.B. proprietäre Operationen) können
  im Hauptpfad nicht getestet werden
- Workaround: `tests/server-specific/` für solche Fälle

## Alternativen verworfen

- **Drei separate Test-Suiten**: Zu hoher Wartungsaufwand
- **Nur ein Server**: Würde Unterschiede unsichtbar machen
