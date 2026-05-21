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

## Option B – Direkter Trigger aus dem MII-Repo

Sobald Schreibzugriff auf `medizininformatik-initiative/kerndatensatzmodul-consent`
besteht, kann ein Workflow dort bei jedem Release automatisch unsere Testsuite
auslösen.

### Schritt 1 – Secret im MII-Repo anlegen

Im MII-Repo unter **Settings → Secrets and variables → Actions** ein neues Secret anlegen:

| Name | Wert |
|---|---|
| `CONSENT_TESTSUITE_TOKEN` | Personal Access Token (PAT) mit Scope `workflow` für das Repo `oeme-github/consent-test-suite` |

Den PAT unter `https://github.com/settings/tokens` erstellen (classic token,
Scope `workflow` reicht).

### Schritt 2 – Workflow im MII-Repo anlegen

Neue Datei im MII-Repo: `.github/workflows/notify-consent-testsuite.yml`

```yaml
name: Consent-Testsuite benachrichtigen

on:
  release:
    types: [published]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Consent-Testsuite triggern
        run: |
          curl -sf -X POST \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${{ secrets.CONSENT_TESTSUITE_TOKEN }}" \
            "https://api.github.com/repos/oeme-github/consent-test-suite/actions/workflows/mii-watch.yml/dispatches" \
            -d '{"ref":"main","inputs":{"force_run":"true"}}'
```

### Schritt 3 – Workflow im Testsuite-Repo für `workflow_dispatch` freigeben

`mii-watch.yml` enthält bereits den `workflow_dispatch`-Trigger mit dem
`force_run`-Input – kein weiterer Anpassungsbedarf.

---

## Versionsverfolgung

Die zuletzt erfolgreich getestete MII-Version wird in `.mii-consent-ig-version`
im Root-Verzeichnis dieses Repos gespeichert. Diese Datei wird durch den
`update-version`-Job automatisch aktualisiert.
