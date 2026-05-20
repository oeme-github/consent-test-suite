# FHIR Consent Testumgebung

Automatisierte Testumgebung für FHIR Consent gemäß
[MII Broad Consent Profil](https://simplifier.net/MedizininformatikInitiative-ModulConsent).

Entwickelt von **HL7germany Arbeitsgruppe Einwilligungsmanagement** und
**MII Task Force Consent Umsetzung**.

---

## Was dieses Repository enthält

- **Fixture-Bibliothek**: Kanonische FHIR Consent-Ressourcen für definierte Testszenarien
- **Testfall-Katalog**: Conformance-Tests und Search-Parameter-Tests
- **Infrastruktur**: Docker Compose für HAPI FHIR, Blaze und Firely Server
- **CI/CD**: Automatische Testausführung bei Änderungen

---

## Schnellstart

```bash
# 1. Server starten
docker compose -f infrastructure/docker-compose.yml up -d

# 2. Fixtures laden
./infrastructure/setup.sh

# 3. Tests ausführen (gegen alle drei Server)
./run-tests.sh
```

Ausführlichere Anleitung: [docs/getting-started.md](docs/getting-started.md)

---

## Testabdeckung

| Kategorie | Beschreibung |
|---|---|
| **Conformance** | Validierung gegen MII Consent IG-Profile |
| **Search** | FHIR Search-Parameter (patient, status, category, date, actor, …) |
| **Server-spezifisch** | Dokumentierte Unterschiede zwischen HAPI, Blaze, Firely |

Vollständiger Testfall-Katalog: [tests/README.md](tests/README.md)

---

## Beitragen

Fehler gefunden oder Testfall fehlt? Issues und Pull Requests sind willkommen.

Beim Hinzufügen neuer Testfälle bitte die Konventionen in
[tests/README.md](tests/README.md) beachten.

---

## Lizenz

> ⚠️ TODO: Lizenz ergänzen
