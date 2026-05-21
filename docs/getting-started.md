# Getting Started

Diese Anleitung gilt für **Linux** (VPS, Server) und **Windows mit WSL2**.
Beides verhält sich identisch — alle Skripte laufen nativ in der Bash-Umgebung.

---

## Voraussetzungen

### Linux (Ubuntu/Debian)

```bash
# Docker Engine
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # Neuanmeldung danach erforderlich

# Node.js 20 + Newman
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs
npm install -g newman newman-reporter-junitfull

# curl und python3 sind auf Ubuntu/Debian bereits vorhanden
```

### Windows mit WSL2

**Schritt 1 – WSL2 einrichten** (einmalig, als Administrator in PowerShell):
```powershell
wsl --install          # installiert Ubuntu als Standard-Distro
# danach: Neustart, Ubuntu-Benutzername und Passwort festlegen
```

**Schritt 2 – Docker Desktop installieren**
- [Docker Desktop herunterladen](https://www.docker.com/products/docker-desktop/)
- Während der Installation: "Use WSL2 based engine" aktivieren
- Nach dem Start: **Settings → Resources → WSL Integration** → Ubuntu aktivieren

**Schritt 3 – Im Ubuntu-WSL-Terminal:**
```bash
# Node.js 20 + Newman
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs
npm install -g newman newman-reporter-junitfull

# python3 und curl sind bereits vorhanden
```

**Prüfen ob alles bereit ist:**
```bash
docker --version          # z.B. Docker version 27.x.x
docker compose version    # z.B. Docker Compose version v2.x.x
newman --version          # z.B. 6.x.x
python3 --version         # z.B. Python 3.10.x
```

---

## Testumgebung starten

### 1. Repository klonen

```bash
git clone https://github.com/oeme-github/consent-test-suite.git
cd consent-test-suite
```

### 2. Server starten

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

Beim **ersten Start** werden Images heruntergeladen (~2–4 GB, einmalig).
HAPI benötigt ca. **90 Sekunden** zum Hochfahren. Status prüfen:

```bash
docker compose -f infrastructure/docker-compose.yml ps
```

Alle drei Server sind bereit, wenn der Status `healthy` anzeigt.

### 3. Fixtures laden

```bash
chmod +x infrastructure/setup.sh
./infrastructure/setup.sh           # alle drei Server
./infrastructure/setup.sh hapi      # nur HAPI
./infrastructure/setup.sh blaze     # nur Blaze
./infrastructure/setup.sh firely    # nur Firely (siehe Hinweis unten)
```

Das Skript lädt in dieser Reihenfolge:
1. MII SearchParameter (6 Custom-SPs)
2. Test-Patienten (5 Patient-Ressourcen)
3. Test-Consents (5 Consent-Ressourcen)

### 4. Tests ausführen

```bash
chmod +x run-tests.sh
./run-tests.sh           # alle drei Server
./run-tests.sh hapi      # nur HAPI
./run-tests.sh blaze     # nur Blaze
./run-tests.sh firely    # nur Firely
```

Ergebnisse werden als JUnit-XML in `test-results/` gespeichert.

---

## Server-URLs

| Server | FHIR-Basis | Metadata |
|---|---|---|
| HAPI FHIR | `http://localhost:8080/fhir` | http://localhost:8080/fhir/metadata |
| Blaze | `http://localhost:8081/fhir` | http://localhost:8081/fhir/metadata |
| Firely | `http://localhost:8082/fhir` | http://localhost:8082/fhir/metadata |

Unter WSL2 sind diese URLs auch direkt im Windows-Browser erreichbar.

---

## Hinweise

### Firely Server – Lizenz erforderlich

Firely Server startet ohne Lizenz im eingeschränkten Modus — Schreib-Operationen
und viele Suchen werden abgelehnt. Für vollständige Tests ist eine Lizenz nötig:

```bash
# Lizenzdatei als Umgebungsvariable setzen (vor docker compose up):
export FIRELY_LICENSE_JSON=$(cat /pfad/zur/firely-license.json)
```

Für HAPI und Blaze ist keine Lizenz erforderlich.

### Kompletter Reset

```bash
docker compose -f infrastructure/docker-compose.yml down -v
```

Löscht alle Container **und** Volumes (Datenbank-Inhalte). Danach wieder
`setup.sh` ausführen.

### Nur bestimmten Server zurücksetzen

```bash
./infrastructure/setup.sh hapi   # löscht Test-Fixtures und lädt sie neu
```

`setup.sh` bereinigt bestehende Test-Daten vor dem Laden automatisch.

---

## Schnelltest (HAPI, 3 Befehle)

```bash
docker compose -f infrastructure/docker-compose.yml up -d
sleep 90 && ./infrastructure/setup.sh hapi
./run-tests.sh hapi
```
