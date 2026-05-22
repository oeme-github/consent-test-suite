#!/usr/bin/env python3
"""Rebuild TC-UPDATE-001 and TC-UPDATE-002 to use 4 Consents (permit→deny one by one)."""
import json, sys

COLLECTION = "tests/search/collection.json"
PATIENT    = "Patient/test-patient-update-001"
CODE_TYPE  = ("urn:oid:2.16.840.1.113883.3.1937.777.24.5.3"
              "%7C2.16.840.1.113883.3.1937.777.24.5.3.7%24permit")
IDS = [f"mii-consent-update-test-{str(n).zfill(3)}" for n in range(1, 5)]

# ── FHIR resource ────────────────────────────────────────────────────────────

def consent_body(cid, ptype):
    return json.dumps({
        "resourceType": "Consent", "id": cid,
        "meta": {
            "profile": ["https://www.medizininformatik-initiative.de/fhir/modul-consent/"
                        "StructureDefinition/mii-pr-consent-einwilligung"],
            "tag": [{"system": "https://www.medizininformatik-initiative.de/fhir/modul-consent/"
                               "CodeSystem/Tags", "code": "test-fixture"}]
        },
        "status": "active",
        "scope": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/consentscope",
                               "code": "research"}]},
        "category": [
            {"coding": [{"system": "http://loinc.org", "code": "57016-8"}]},
            {"coding": [{"system": "https://www.medizininformatik-initiative.de/fhir/modul-consent/"
                                   "CodeSystem/mii-cs-consent-consent_category",
                         "code": "2.16.840.1.113883.3.1937.777.24.2.184"}]}
        ],
        "patient": {"reference": PATIENT},
        "dateTime": "2024-03-01",
        "organization": [{"display": "Klinikum Musterstadt"}],
        "policy": [{"uri": "urn:oid:2.16.840.1.113883.3.1937.777.24.2.1791"}],
        "provision": {
            "type": "deny",
            "period": {"start": "2024-03-01", "end": "2054-03-01"},
            "provision": [{
                "type": ptype,
                "period": {"start": "2024-03-01", "end": "2054-03-01"},
                "code": [{"coding": [{"system": "urn:oid:2.16.840.1.113883.3.1937.777.24.5.3",
                                      "code": "2.16.840.1.113883.3.1937.777.24.5.3.7",
                                      "display": "MDAT speichern verarbeiten"}]}]
            }]
        }
    }, ensure_ascii=False, separators=(',', ':'))

# ── URL helpers ───────────────────────────────────────────────────────────────

def search_url(refresh=False):
    raw = "{{baseUrl}}/Consent?patient=" + PATIENT + "&mii-provision-provision-code-type=" + CODE_TYPE
    query = [{"key": "patient", "value": PATIENT},
             {"key": "mii-provision-provision-code-type", "value": CODE_TYPE}]
    if refresh:
        raw += "&_refresh=true"
        query.append({"key": "_refresh", "value": "true"})
    return {"raw": raw, "host": ["{{baseUrl}}"], "path": ["Consent"], "query": query}

def consent_url(cid):
    return {"raw": "{{baseUrl}}/Consent/" + cid,
            "host": ["{{baseUrl}}"], "path": ["Consent", cid]}

# ── Request builders ──────────────────────────────────────────────────────────

def put_req(cid, ptype):
    return {"method": "PUT",
            "header": [{"key": "Content-Type", "value": "application/fhir+json"},
                       {"key": "Accept",       "value": "application/fhir+json"}],
            "body": {"mode": "raw", "raw": consent_body(cid, ptype),
                     "options": {"raw": {"language": "json"}}},
            "url": consent_url(cid)}

def delete_req(cid):
    return {"method": "DELETE",
            "header": [{"key": "Accept", "value": "application/fhir+json"}],
            "url": consent_url(cid)}

def get_req(refresh=False):
    return {"method": "GET",
            "header": [{"key": "Accept", "value": "application/fhir+json"}],
            "url": search_url(refresh)}

# ── Test-script helpers ───────────────────────────────────────────────────────

def test_2xx(codes="[200, 201]", msg="HTTP 2xx"):
    return [f"pm.test('{msg}', function () {{",
            f"  pm.expect(pm.response.code).to.be.oneOf({codes});",
            "});"]

def test_total(n, label):
    return [f"pm.test('{label}', function () {{",
            "  var json = pm.response.json();",
            f"  pm.expect(json.total).to.equal({n});",
            "});"]

def test_assert_block(n, after_id, refresh):
    refresh_hint = " (mit _refresh=true)" if refresh else ""
    return (
        ["pm.test('HTTP 200 OK', function () {",
         "  pm.response.to.have.status(200);",
         "});",
         "",
         "pm.test('Response ist Bundle', function () {",
         "  var json = pm.response.json();",
         "  pm.expect(json.resourceType).to.equal('Bundle');",
         "});",
         ""]
        + test_total(n,
            f"Suchindex aktualisiert{refresh_hint}: nach Update {after_id} → .3.7$permit total: {n}")
    )

def event(exec_lines):
    return [{"listen": "test",
             "script": {"type": "text/javascript", "exec": exec_lines}}]

# ── Item builders ─────────────────────────────────────────────────────────────

def setup_item(cid):
    return {"name": f"[Setup] PUT – {cid} anlegen (.3.7 = permit)",
            "event": event(test_2xx("[200, 201]", "HTTP 200 oder 201 (Consent angelegt)")),
            "request": put_req(cid, "permit")}

def verify_item():
    return {"name": "[Verify] GET – alle 4 Consents per .3.7$permit auffindbar (total: 4)",
            "event": event(
                ["pm.test('HTTP 200 OK', function () {",
                 "  pm.response.to.have.status(200);",
                 "});",
                 ""]
                + test_total(4, "Vorbedingung: 4 Consents per .3.7$permit auffindbar")),
            "request": get_req()}

def act_item(cid):
    return {"name": f"[Act] PUT – {cid}: .3.7 auf deny setzen",
            "event": event(test_2xx("[200]", "HTTP 200 OK (Update erfolgreich)")),
            "request": put_req(cid, "deny")}

def assert_item(n, after_id, refresh=False):
    refresh_label = " mit _refresh=true" if refresh else ""
    return {"name": f"[Assert] GET{refresh_label} – nach Update {after_id}: .3.7$permit → total: {n}",
            "event": event(test_assert_block(n, after_id, refresh)),
            "request": get_req(refresh)}

def cleanup_item(cid):
    return {"name": f"[Cleanup] DELETE – {cid} entfernen",
            "event": event(test_2xx("[200, 204]", "HTTP 200 oder 204 (Consent gelöscht)")),
            "request": delete_req(cid)}

# ── Build test cases ──────────────────────────────────────────────────────────

def build_tc(name, refresh):
    items = []
    for cid in IDS:
        items.append(setup_item(cid))
    items.append(verify_item())
    for i, cid in enumerate(IDS):
        items.append(act_item(cid))
        items.append(assert_item(3 - i, cid, refresh))
    for cid in IDS:
        items.append(cleanup_item(cid))
    return {"name": name, "item": items}

TC_001 = build_tc(
    "TC-UPDATE-001: Search-Konsistenz nach PUT (permit→deny) – 4 Datensätze", refresh=False)
TC_002 = build_tc(
    "TC-UPDATE-002: Search-Konsistenz nach PUT mit _refresh – 4 Datensätze", refresh=True)

# ── Inject into collection ────────────────────────────────────────────────────

with open(COLLECTION) as f:
    col = json.load(f)

replaced = {1: False, 2: False}
for i, item in enumerate(col["item"]):
    name = item.get("name", "")
    if name.startswith("TC-UPDATE-001"):
        col["item"][i] = TC_001
        replaced[1] = True
    elif name.startswith("TC-UPDATE-002"):
        col["item"][i] = TC_002
        replaced[2] = True

if not all(replaced.values()):
    print("ERROR: TC-UPDATE-001 oder TC-UPDATE-002 nicht gefunden", file=sys.stderr)
    sys.exit(1)

with open(COLLECTION, "w") as f:
    json.dump(col, f, indent=2, ensure_ascii=False)

# Summary
print(f"TC-UPDATE-001: {len(TC_001['item'])} Requests")
print(f"TC-UPDATE-002: {len(TC_002['item'])} Requests")
print("collection.json aktualisiert.")
