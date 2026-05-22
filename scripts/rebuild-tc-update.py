#!/usr/bin/env python3
"""Rebuild TC-UPDATE-001/002/003 in collection.json.

TC-UPDATE-001: 4 Consents (.3.7=permit), einzeln auf deny setzen → total 4→3→2→1→0
TC-UPDATE-002: wie 001, aber Assert-Suchen mit _refresh=true
TC-UPDATE-003: Issue-#123-Replikation – 4 Consents (.3.7=permit UND .3.8=permit),
               .3.7 einzeln auf deny → Suche mit BEIDEN Params muss schrumpfen
"""
import json, sys

COLLECTION = "tests/search/collection.json"
PATIENT    = "Patient/test-patient-update-001"
OID        = "urn:oid:2.16.840.1.113883.3.1937.777.24.5.3"
CODE_37    = f"{OID}%7C{OID}.7%24permit"
CODE_38    = f"{OID}%7C{OID}.8%24permit"
IDS        = [f"mii-consent-update-test-{str(n).zfill(3)}" for n in range(1, 5)]

# ── FHIR resource builders ────────────────────────────────────────────────────

def _base(cid):
    return {
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
        "policy": [{"uri": f"{OID.replace('urn:oid:', 'urn:oid:')}".replace(
            "urn:oid:2.16.840.1.113883.3.1937.777.24.5.3",
            "urn:oid:2.16.840.1.113883.3.1937.777.24.2.1791")}],
    }

def _provision_entry(code_suffix, ptype):
    return {
        "type": ptype,
        "period": {"start": "2024-03-01", "end": "2054-03-01"},
        "code": [{"coding": [{"system": OID,
                               "code": f"{OID}.{code_suffix}",
                               "display": {"7": "MDAT speichern verarbeiten",
                                           "8": "MDAT wissenschaftlich nutzen EU DSGVO konform"
                                           }.get(code_suffix, code_suffix)}]}]
    }

def consent_body_single(cid, ptype_37):
    """Consent mit nur .3.7 – für TC-UPDATE-001/002."""
    r = _base(cid)
    r["provision"] = {
        "type": "deny",
        "period": {"start": "2024-03-01", "end": "2054-03-01"},
        "provision": [_provision_entry("7", ptype_37)]
    }
    return json.dumps(r, ensure_ascii=False, separators=(',', ':'))

def consent_body_dual(cid, ptype_37, ptype_38="permit"):
    """Consent mit .3.7 und .3.8 – für TC-UPDATE-003 (Issue-#123-Szenario)."""
    r = _base(cid)
    r["provision"] = {
        "type": "deny",
        "period": {"start": "2024-03-01", "end": "2054-03-01"},
        "provision": [
            _provision_entry("7", ptype_37),
            _provision_entry("8", ptype_38),
        ]
    }
    return json.dumps(r, ensure_ascii=False, separators=(',', ':'))

# ── URL helpers ───────────────────────────────────────────────────────────────

def consent_url(cid):
    return {"raw": "{{baseUrl}}/Consent/" + cid,
            "host": ["{{baseUrl}}"], "path": ["Consent", cid]}

def search_url_single(refresh=False):
    raw = f"{{{{baseUrl}}}}/Consent?patient={PATIENT}&mii-provision-provision-code-type={CODE_37}"
    query = [{"key": "patient", "value": PATIENT},
             {"key": "mii-provision-provision-code-type", "value": CODE_37}]
    if refresh:
        raw += "&_refresh=true"
        query.append({"key": "_refresh", "value": "true"})
    return {"raw": raw, "host": ["{{baseUrl}}"], "path": ["Consent"], "query": query}

def search_url_dual(refresh=False):
    """Beide Params: .3.7$permit UND .3.8$permit (Issue-#123-Szenario)."""
    raw = (f"{{{{baseUrl}}}}/Consent?patient={PATIENT}"
           f"&mii-provision-provision-code-type={CODE_37}"
           f"&mii-provision-provision-code-type={CODE_38}")
    query = [{"key": "patient", "value": PATIENT},
             {"key": "mii-provision-provision-code-type", "value": CODE_37},
             {"key": "mii-provision-provision-code-type", "value": CODE_38}]
    if refresh:
        raw += "&_refresh=true"
        query.append({"key": "_refresh", "value": "true"})
    return {"raw": raw, "host": ["{{baseUrl}}"], "path": ["Consent"], "query": query}

# ── Request builders ──────────────────────────────────────────────────────────

def put_req(cid, body_str):
    return {"method": "PUT",
            "header": [{"key": "Content-Type", "value": "application/fhir+json"},
                       {"key": "Accept",       "value": "application/fhir+json"}],
            "body": {"mode": "raw", "raw": body_str,
                     "options": {"raw": {"language": "json"}}},
            "url": consent_url(cid)}

def delete_req(cid):
    return {"method": "DELETE",
            "header": [{"key": "Accept", "value": "application/fhir+json"}],
            "url": consent_url(cid)}

def get_req(url_fn, refresh=False):
    return {"method": "GET",
            "header": [{"key": "Accept", "value": "application/fhir+json"}],
            "url": url_fn(refresh)}

# ── Test-script helpers ───────────────────────────────────────────────────────

def event(exec_lines):
    return [{"listen": "test", "script": {"type": "text/javascript", "exec": exec_lines}}]

def test_2xx(codes, msg):
    return [f"pm.test('{msg}', function () {{",
            f"  pm.expect(pm.response.code).to.be.oneOf({codes});",
            "});"]

def test_assert_block(n, after_id, refresh, label_suffix=""):
    hint = " (mit _refresh=true)" if refresh else ""
    return (["pm.test('HTTP 200 OK', function () {",
             "  pm.response.to.have.status(200);",
             "});",
             "",
             "pm.test('Response ist Bundle', function () {",
             "  var json = pm.response.json();",
             "  pm.expect(json.resourceType).to.equal('Bundle');",
             "});",
             ""]
            + [f"pm.test('Suchindex aktualisiert{hint}: nach Update {after_id}{label_suffix} → total: {n}', function () {{",
               "  var json = pm.response.json();",
               f"  pm.expect(json.total).to.equal({n});",
               "});"])

# ── Generic item builders ─────────────────────────────────────────────────────

def setup_item(cid, body_str, label):
    return {"name": f"[Setup] PUT – {cid} anlegen ({label})",
            "event": event(test_2xx("[200, 201]", "HTTP 200 oder 201 (Consent angelegt)")),
            "request": put_req(cid, body_str)}

def verify_item(total, url_fn, label):
    return {"name": f"[Verify] GET – {label} (total: {total})",
            "event": event(
                ["pm.test('HTTP 200 OK', function () {",
                 "  pm.response.to.have.status(200);",
                 "});",
                 ""]
                + [f"pm.test('Vorbedingung: {label}', function () {{",
                   "  var json = pm.response.json();",
                   f"  pm.expect(json.total).to.equal({total});",
                   "});"]),
            "request": get_req(url_fn)}

def act_item(cid, body_str, label):
    return {"name": f"[Act] PUT – {cid}: {label}",
            "event": event(test_2xx("[200]", "HTTP 200 OK (Update erfolgreich)")),
            "request": put_req(cid, body_str)}

def assert_item(n, after_id, url_fn, refresh=False, label_suffix=""):
    refresh_label = " mit _refresh=true" if refresh else ""
    return {"name": f"[Assert] GET{refresh_label} – nach Update {after_id}: total: {n}",
            "event": event(test_assert_block(n, after_id, refresh, label_suffix)),
            "request": get_req(url_fn, refresh)}

def cleanup_item(cid):
    return {"name": f"[Cleanup] DELETE – {cid} entfernen",
            "event": event(test_2xx("[200, 204]", "HTTP 200 oder 204 (Consent gelöscht)")),
            "request": delete_req(cid)}

# ── Build TC-UPDATE-001 / 002 (single param: .3.7$permit) ────────────────────

def build_tc_single(name, refresh):
    items = []
    for cid in IDS:
        items.append(setup_item(cid, consent_body_single(cid, "permit"), ".3.7 = permit"))
    items.append(verify_item(4, search_url_single, "4 Consents per .3.7$permit auffindbar"))
    for i, cid in enumerate(IDS):
        items.append(act_item(cid, consent_body_single(cid, "deny"), ".3.7 auf deny setzen"))
        items.append(assert_item(3 - i, cid, search_url_single, refresh))
    for cid in IDS:
        items.append(cleanup_item(cid))
    return {"name": name, "item": items}

# ── Build TC-UPDATE-003 (dual params: .3.7$permit AND .3.8$permit) ────────────

def build_tc_003():
    items = []
    for cid in IDS:
        items.append(setup_item(cid, consent_body_dual(cid, "permit", "permit"),
                                ".3.7 = permit, .3.8 = permit"))
    items.append(verify_item(4, search_url_dual,
                             "4 Consents per .3.7$permit UND .3.8$permit auffindbar"))
    for i, cid in enumerate(IDS):
        items.append(act_item(cid, consent_body_dual(cid, "deny", "permit"),
                              ".3.7 auf deny setzen (.3.8 bleibt permit)"))
        items.append(assert_item(3 - i, cid, search_url_dual, refresh=False,
                                 label_suffix=" (.3.7$permit AND .3.8$permit)"))
    for cid in IDS:
        items.append(cleanup_item(cid))
    return {
        "name": ("TC-UPDATE-003: Issue-#123-Replikation – "
                 "AND-Suche .3.7$permit+.3.8$permit nach PUT .3.7→deny"),
        "item": items
    }

# ── Inject into collection ────────────────────────────────────────────────────

TC_001 = build_tc_single(
    "TC-UPDATE-001: Search-Konsistenz nach PUT (permit→deny) – 4 Datensätze", refresh=False)
TC_002 = build_tc_single(
    "TC-UPDATE-002: Search-Konsistenz nach PUT mit _refresh – 4 Datensätze", refresh=True)
TC_003 = build_tc_003()

with open(COLLECTION) as f:
    col = json.load(f)

replaced = {1: False, 2: False, 3: False}
for i, item in enumerate(col["item"]):
    name = item.get("name", "")
    if name.startswith("TC-UPDATE-001"):
        col["item"][i] = TC_001; replaced[1] = True
    elif name.startswith("TC-UPDATE-002"):
        col["item"][i] = TC_002; replaced[2] = True
    elif name.startswith("TC-UPDATE-003"):
        col["item"][i] = TC_003; replaced[3] = True

if not replaced[3]:
    col["item"].append(TC_003)
    replaced[3] = True

if not all(replaced.values()):
    missing = [k for k, v in replaced.items() if not v]
    print(f"ERROR: TC-UPDATE-{missing} nicht gefunden/eingefügt", file=sys.stderr)
    sys.exit(1)

with open(COLLECTION, "w") as f:
    json.dump(col, f, indent=2, ensure_ascii=False)

print(f"TC-UPDATE-001: {len(TC_001['item'])} Requests")
print(f"TC-UPDATE-002: {len(TC_002['item'])} Requests")
print(f"TC-UPDATE-003: {len(TC_003['item'])} Requests")
print("collection.json aktualisiert.")
