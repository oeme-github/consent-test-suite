#!/usr/bin/env bash
# run-tests.sh – Alle Tests gegen alle drei FHIR-Server ausführen
# Verwendung: ./run-tests.sh [hapi|blaze|firely|all]
# Standard: alle drei Server

set -euo pipefail

HAPI_URL="${FHIR_BASE_HAPI:-http://localhost:8080/fhir}"
BLAZE_URL="${FHIR_BASE_BLAZE:-http://localhost:8081/fhir}"
FIRELY_URL="${FHIR_BASE_FIRELY:-http://localhost:8082/fhir}"

TARGET="${1:-all}"
RESULTS_DIR="test-results"
FAILED=0

mkdir -p "$RESULTS_DIR"

# ── Hilfsfunktionen ─────────────────────────────────────────────────────────

run_search_tests() {
  local url="$1"
  local name="$2"
  local slug
  slug=$(echo "$name" | tr '[:upper:] ' '[:lower:]-')

  echo "🔍 Search-Tests gegen $name ($url)..."
  if newman run tests/search/collection.json \
    --env-var "baseUrl=$url" \
    --reporters cli,junitfull \
    --reporter-junitfull-export "$RESULTS_DIR/search-$slug.xml"; then
    echo "✅ Search-Tests $name: PASS"
  else
    echo "❌ Search-Tests $name: FAIL"
    FAILED=$((FAILED + 1))
  fi
  echo ""
}

# ── Hauptprogramm ────────────────────────────────────────────────────────────

echo "================================================"
echo " FHIR Consent Testumgebung – Testausführung"
echo "================================================"
echo ""
echo "Ergebnisse werden gespeichert in: $RESULTS_DIR/"
echo ""

case "$TARGET" in
  hapi)
    run_search_tests "$HAPI_URL" "HAPI FHIR"
    ;;
  blaze)
    run_search_tests "$BLAZE_URL" "Blaze"
    ;;
  firely)
    run_search_tests "$FIRELY_URL" "Firely"
    ;;
  all)
    run_search_tests "$HAPI_URL"   "HAPI FHIR"
    run_search_tests "$BLAZE_URL"  "Blaze"
    run_search_tests "$FIRELY_URL" "Firely"
    ;;
  *)
    echo "Unbekannter Server: $TARGET"
    echo "Verwendung: $0 [hapi|blaze|firely|all]"
    exit 1
    ;;
esac

echo "================================================"
if [ "$FAILED" -eq 0 ]; then
  echo " ✅ Alle Tests bestanden."
else
  echo " ❌ $FAILED Testlauf/läufe fehlgeschlagen."
fi
echo "================================================"

exit "$FAILED"
