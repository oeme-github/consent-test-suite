# ADR-0002: Fixture-Strategie

## Status
Akzeptiert

## Kontext

Fehlermeldungen aus der Community waren oft schwer reproduzierbar, weil
der Serverstand zum Zeitpunkt des Fehlers unbekannt war. Tests müssen
von einem **definierten, reproduzierbaren Ausgangszustand** starten.

## Entscheidung

Alle Testdaten werden als **FHIR JSON-Fixtures** im Repository versioniert.
Vor jedem Testlauf (lokal und CI) wird der Server in einen definierten
Zustand gebracht:

1. Alle vorhandenen Consent-Ressourcen löschen (`DELETE` oder Server-Neustart)
2. Fixtures aus `fixtures/valid/` und `fixtures/invalid/` laden (`POST`)

Fixtures sind nach **Szenarien** benannt, nicht nach technischen IDs:

```
fixtures/
├── valid/
│   ├── consent-broad-erteilt.json
│   ├── consent-broad-widerrufen.json
│   ├── consent-spezifisch-studie-a.json
│   └── consent-expired.json
└── invalid/
    ├── consent-missing-patient.json
    ├── consent-unknown-policy.json
    └── consent-invalid-status.json
```

Jede Fixture enthält im `meta.tag`-Feld das Tag `test-fixture`,
damit sie im Setup-Skript zuverlässig identifiziert und bereinigt
werden kann.

## Konsequenzen

**Positiv:**
- Vollständige Reproduzierbarkeit von Fehlern
- Fixtures dienen gleichzeitig als Dokumentation valider/invalider Consents
- Community kann Fixtures als Referenzimplementierung nutzen

**Negativ / Einschränkungen:**
- Fixtures müssen bei IG-Versionswechseln aktualisiert werden
- Fixture-IDs sind fix – bei Serverneustarts kann es zu ID-Konflikten kommen
  (Workaround: `setup.sh` löscht immer zuerst)

## Versionshinweis

Fixtures sind gegen eine spezifische IG-Version entwickelt. Die
unterstützte Version steht in `fixtures/README.md`.
