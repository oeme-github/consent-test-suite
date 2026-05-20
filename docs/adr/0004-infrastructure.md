# ADR-0004: Infrastruktur (Docker Compose)

## Status
Akzeptiert

## Kontext

Tests müssen lokal und in CI identisch reproduzierbar laufen.
Serverversionen dürfen sich nicht implizit ändern.

## Entscheidung

Alle drei FHIR-Server werden per **Docker Compose** mit **fixen
Image-Tags** betrieben. `latest` wird nie verwendet.

```yaml
# Beispiel: immer explizite Version
image: hapiproject/hapi:v7.4.0
```

Versionsupgrades sind explizite Pull-Requests, die automatisch
alle Tests gegen die neue Version ausführen.

## Konsequenzen

**Positiv:**
- Vollständige Reproduzierbarkeit lokal ↔ CI
- Versionsupgrades sind kontrolliert und nachvollziehbar
- Keine Überraschungen durch automatische Updates

**Negativ / Einschränkungen:**
- Manuelle Pflege der Versionen erforderlich
- Lokaler Speicherbedarf für drei Docker-Images (~2–4 GB)
