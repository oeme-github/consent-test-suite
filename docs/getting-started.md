# Getting Started

## Voraussetzungen

- Docker & Docker Compose
- `curl` und `python3` (für `setup.sh`)
- Node.js 18+ und `newman` (für Test-Ausführung)

```bash
npm install -g newman newman-reporter-junitfull
```

---

## Lokaler Start

### 1. Server starten

```bash
docker compose -f infrastructure/docker-compose.yml up -d
```

Alle drei Server starten parallel. Beim ersten Start werden Images
heruntergeladen (~2–4 GB). Status prüfen:

```bash
docker compose -f infrastructure/docker-compose.yml ps
```

### 2. Fixtures laden

```bash
chmod +x infrastructure/setup.sh
./infrastructure/setup.sh           # alle drei Server
./infrastructure/setup.sh hapi      # nur HAPI
./infrastructure/setup.sh blaze     # nur Blaze
./infrastructure/setup.sh firely    # nur Firely
```

### 3. Tests ausführen

```bash
# Search-Tests gegen HAPI
newman run tests/search/collection.json \
  --env-var "baseUrl=http://localhost:8080/fhir"

# Search-Tests gegen Blaze
newman run tests/search/collection.json \
  --env-var "baseUrl=http://localhost:8081/fhir"
```

---

## Server-URLs (lokal)

| Server | URL | Metadata |
|---|---|---|
| HAPI FHIR | `http://localhost:8080/fhir` | [öffnen](http://localhost:8080/fhir/metadata) |
| Blaze | `http://localhost:8081/fhir` | [öffnen](http://localhost:8081/fhir/metadata) |
| Firely | `http://localhost:8082/fhir` | [öffnen](http://localhost:8082/fhir/metadata) |

---

## Server stoppen

```bash
docker compose -f infrastructure/docker-compose.yml down
```

Daten löschen (kompletter Reset):

```bash
docker compose -f infrastructure/docker-compose.yml down -v
```
