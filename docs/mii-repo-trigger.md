# Trigger aus dem MII Kerndatensatzmodul-Consent Repo

## Überblick

Die Testsuite prüft automatisch, ob eine neue Version des MII Consent Implementation
Guide veröffentlicht wurde (Option A: Release-Watch via GitHub Actions).

Sobald Zugang zum MII-Repo besteht, kann zusätzlich ein direkter Trigger aus dem
Upstream-Repo eingerichtet werden (Option B: `repository_dispatch`).

---

## Option A – Release-Watch (aktiv)

Datei: `.github/workflows/mii-watch.yml`

Der Workflow läuft jeden Montag um 06:00 UTC und vergleicht den aktuellen Release-Tag
des MII-Repos mit der zuletzt getesteten Version (gespeichert in `.mii-consent-ig-version`).

**Ablauf:**
1. GitHub API abfragen: `GET /repos/medizininformatik-initiative/kerndatensatzmodul-consent/releases/latest`
2. Tag mit `.mii-consent-ig-version` vergleichen
3. Bei Abweichung: Tests gegen HAPI und Blaze ausführen
4. Nach erfolgreichem Testlauf: `.mii-consent-ig-version` aktualisieren und committen

**Manuell auslösen:**
```
GitHub → Actions → "MII Consent IG – Release Watch" → Run workflow
```
Mit der Option "Tests erzwingen" können Tests auch ohne neue MII-Version gestartet werden.

---

## Option B – Direkter Trigger aus dem MII-Repo (implementiert)

`mii-watch.yml` reagiert auf den `repository_dispatch`-Event `mii-consent-ig-released`.
Das MII-Repo sendet diesen Event bei jedem neuen Release. Die Version wird als
`client_payload.version` übergeben und direkt als getestete Version verwendet —
kein zusätzlicher API-Call nötig.

### Schritt 1 – Secret im MII-Repo anlegen

Im MII-Repo unter **Settings → Secrets and variables → Actions** ein neues Secret anlegen:

| Name | Wert |
|---|---|
| `CONSENT_TESTSUITE_TOKEN` | Personal Access Token (PAT) mit Scope `repo` für `oeme-github/consent-test-suite` |

Den PAT unter `https://github.com/settings/tokens` erstellen (classic token,
Scope `repo`; oder Fine-grained token mit "Contents: Read & Write" auf diesem Repo).

### Schritt 2 – Workflow im MII-Repo anlegen

Fertiges Template: `docs/mii-repo-notify-workflow.yml` in diesem Repository.

Die Datei unter `.github/workflows/notify-consent-testsuite.yml` im MII-Repo ablegen.

**Kurzfassung des Templates:**
```yaml
on:
  release:
    types: [published]
jobs:
  notify:
    steps:
      - run: |
          curl -sf -X POST \
            -H "Authorization: Bearer ${{ secrets.CONSENT_TESTSUITE_TOKEN }}" \
            "https://api.github.com/repos/oeme-github/consent-test-suite/dispatches" \
            -d '{"event_type":"mii-consent-ig-released","client_payload":{"version":"${{ github.event.release.tag_name }}"}}'
```

### Schritt 3 – Kein weiterer Anpassungsbedarf

`mii-watch.yml` enthält bereits den `repository_dispatch`-Trigger für
`mii-consent-ig-released` und wertet `client_payload.version` aus.

---

## Versionsverfolgung

Die zuletzt erfolgreich getestete MII-Version wird in `.mii-consent-ig-version`
im Root-Verzeichnis dieses Repos gespeichert. Diese Datei wird durch den
`update-version`-Job automatisch aktualisiert.
