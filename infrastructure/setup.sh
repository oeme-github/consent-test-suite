#!/usr/bin/env bash
# setup.sh – Server in definierten Zustand bringen
# Verwendung: ./infrastructure/setup.sh [--server hapi|blaze|firely|all]
# Standard: alle drei Server

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIXTURES_DIR="$SCRIPT_DIR/../fixtures/valid"

HAPI_URL="${FHIR_BASE_HAPI:-http://localhost:8080/fhir}"
BLAZE_URL="${FHIR_BASE_BLAZE:-http://localhost:8081/fhir}"
FIRELY_URL="${FHIR_BASE_FIRELY:-http://localhost:8082/fhir}"

TARGET="${1:-all}"

# ── Hilfsfunktionen ─────────────────────────────────────────────────────────

wait_for_server() {
  local url="$1"
  local name="$2"
  echo "⏳ Warte auf $name ($url/metadata)..."
  for i in {1..30}; do
    if curl -sf "$url/metadata" > /dev/null 2>&1; then
      echo "✅ $name ist bereit."
      return 0
    fi
    sleep 5
  done
  echo "❌ $name nicht erreichbar nach 150s. Abbruch."
  exit 1
}

delete_test_fixtures() {
  local url="$1"
  local name="$2"
  echo "🗑  Lösche bestehende Test-Fixtures auf $name..."
  # Suche alle Consents mit test-fixture Tag und lösche sie
  local ids
  ids=$(curl -sf "$url/Consent?_tag=test-fixture&_elements=id&_count=100" \
    -H "Accept: application/fhir+json" \
    | python3 -c "
import json,sys
bundle = json.load(sys.stdin)
ids = [e['resource']['id'] for e in bundle.get('entry', [])]
print('\n'.join(ids))
" 2>/dev/null || true)

  if [ -z "$ids" ]; then
    echo "   Keine Test-Fixtures gefunden."
    return
  fi

  while IFS= read -r id; do
    [ -z "$id" ] && continue
    curl -sf -X DELETE "$url/Consent/$id" > /dev/null \
      && echo "   Gelöscht: Consent/$id" \
      || echo "   ⚠️  Konnte Consent/$id nicht löschen (weiter)"
  done <<< "$ids"
}

load_fixtures() {
  local url="$1"
  local name="$2"
  echo "📥 Lade Fixtures auf $name..."
  for fixture in "$FIXTURES_DIR"/*.json; do
    local filename
    filename=$(basename "$fixture")
    local response
    response=$(curl -sf -X POST "$url/Consent" \
      -H "Content-Type: application/fhir+json" \
      -d @"$fixture" \
      -w "\n%{http_code}" 2>&1) || true

    local http_code
    http_code=$(echo "$response" | tail -1)
    if [[ "$http_code" == "201" || "$http_code" == "200" ]]; then
      echo "   ✅ $filename → HTTP $http_code"
    else
      echo "   ❌ $filename → HTTP $http_code (Fehler)"
    fi
  done
}

setup_server() {
  local url="$1"
  local name="$2"
  wait_for_server "$url" "$name"
  delete_test_fixtures "$url" "$name"
  load_fixtures "$url" "$name"
  echo ""
}

# ── Hauptprogramm ────────────────────────────────────────────────────────────

echo "================================================"
echo " FHIR Consent Testumgebung – Setup"
echo "================================================"
echo ""

case "$TARGET" in
  hapi)   setup_server "$HAPI_URL"   "HAPI FHIR" ;;
  blaze)  setup_server "$BLAZE_URL"  "Blaze" ;;
  firely) setup_server "$FIRELY_URL" "Firely" ;;
  all)
    setup_server "$HAPI_URL"   "HAPI FHIR"
    setup_server "$BLAZE_URL"  "Blaze"
    setup_server "$FIRELY_URL" "Firely"
    ;;
  *)
    echo "Unbekannter Server: $TARGET"
    echo "Verwendung: $0 [hapi|blaze|firely|all]"
    exit 1
    ;;
esac

echo "✅ Setup abgeschlossen."
