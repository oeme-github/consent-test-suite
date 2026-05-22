#!/usr/bin/env python3
"""
Root-Cause-Analyse für bekannte FHIR-Testfehler.

Verwendung:
  python3 scripts/analyze-tc.py --tc TC-UPDATE-003 --server hapi
  python3 scripts/analyze-tc.py --tc TC-UPDATE-003 --url http://localhost:8080/fhir
  python3 scripts/analyze-tc.py --ki KI-006 --server blaze
  python3 scripts/analyze-tc.py --list
"""
import argparse
import json
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime

# ── Konstanten ────────────────────────────────────────────────────────────────
OID    = "urn:oid:2.16.840.1.113883.3.1937.777.24.5.3"
POLICY = "urn:oid:2.16.840.1.113883.3.1937.777.24.2.1791"
PAT    = "Patient/test-patient-analyze-001"

SERVERS = {
    "hapi":  "http://localhost:8080/fhir",
    "blaze": "http://localhost:8081/fhir",
    "spark": "http://localhost:8082/fhir",
}

TC_TO_ANALYSIS = {
    "TC-UPDATE-001": "ki006",
    "TC-UPDATE-002": "ki006",
    "TC-UPDATE-003": "ki006",
    "KI-006":        "ki006",
    "TC-SEARCH-010": "ki002_ki005",
    "TC-SEARCH-011": "ki002_ki005",
    "TC-SEARCH-012": "ki002_ki005",
    "TC-SEARCH-013": "ki002_ki005",
    "TC-SEARCH-014": "ki002_ki005",
    "KI-002":        "ki002_ki005",
    "KI-005":        "ki002_ki005",
}

# ── HTTP-Helfer ───────────────────────────────────────────────────────────────

def _parse_response(resp_bytes):
    try:
        return json.loads(resp_bytes)
    except Exception:
        return {}

def fhir_get(base, path):
    req = urllib.request.Request(
        base + path, headers={"Accept": "application/fhir+json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, _parse_response(r.read())
    except urllib.error.HTTPError as e:
        return e.code, _parse_response(e.read())

def fhir_put(base, path, body):
    data = json.dumps(body, ensure_ascii=False).encode()
    req = urllib.request.Request(
        base + path, data=data, method="PUT",
        headers={"Content-Type": "application/fhir+json",
                 "Accept": "application/fhir+json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, _parse_response(r.read())
    except urllib.error.HTTPError as e:
        return e.code, _parse_response(e.read())

def fhir_post(base, path, body=None):
    data = json.dumps(body, ensure_ascii=False).encode() if body else b""
    req = urllib.request.Request(
        base + path, data=data, method="POST",
        headers={"Content-Type": "application/fhir+json",
                 "Accept": "application/fhir+json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, _parse_response(r.read())
    except urllib.error.HTTPError as e:
        return e.code, _parse_response(e.read())

def fhir_delete(base, path):
    req = urllib.request.Request(
        base + path, method="DELETE",
        headers={"Accept": "application/fhir+json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code

def search_total(base, params):
    """Suche mit Liste von (key, value)-Tuples; gibt (total, ids) zurück."""
    qs = urllib.parse.urlencode(params)
    status, body = fhir_get(base, f"/Consent?{qs}")
    if status != 200:
        return None, []
    entries = [e.get("resource", {}).get("id", "?")
               for e in body.get("entry", [])
               if e.get("resource", {}).get("resourceType") == "Consent"]
    return body.get("total"), entries

# ── Fixture-Builder ───────────────────────────────────────────────────────────

def prov_entry(code_suffix, ptype):
    return {
        "type": ptype,
        "period": {"start": "2024-03-01", "end": "2054-03-01"},
        "code": [{"coding": [{"system": OID, "code": f"{OID}.{code_suffix}"}]}],
    }

def make_consent(cid, provisions):
    return {
        "resourceType": "Consent", "id": cid,
        "meta": {"tag": [{"system": OID, "code": "analyze-probe"}]},
        "status": "active",
        "scope": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/consentscope",
                               "code": "research"}]},
        "category": [{"coding": [{"system": "http://loinc.org", "code": "57016-8"}]}],
        "patient": {"reference": PAT},
        "dateTime": "2024-03-01",
        "organization": [{"display": "analyze-tc"}],
        "policy": [{"uri": POLICY}],
        "provision": {
            "type": "deny",
            "period": {"start": "2024-03-01", "end": "2054-03-01"},
            "provision": provisions,
        },
    }

def ensure_patient(base):
    pid = PAT.split("/")[1]
    status, _ = fhir_get(base, f"/{PAT}")
    if status != 200:
        fhir_put(base, f"/Patient/{pid}", {
            "resourceType": "Patient", "id": pid,
            "name": [{"family": "Analyze", "given": ["Test"]}],
        })

def cleanup(base, ids):
    for cid in ids:
        fhir_delete(base, f"/Consent/{cid}")

# ── Server-Info ───────────────────────────────────────────────────────────────

def get_server_info(base):
    status, meta = fhir_get(base, "/metadata")
    if status != 200:
        return {"name": "unbekannt", "version": "?", "fhir": "?"}
    sw = meta.get("software", {})
    return {
        "name":    sw.get("name", "?"),
        "version": sw.get("version", "?"),
        "fhir":    meta.get("fhirVersion", "?"),
    }

# ── Report-Zeilen ─────────────────────────────────────────────────────────────

def row(icon, msg): return f"  {icon} {msg}"
def ok(msg):        return row("✅", msg)
def fail(msg):      return row("❌", msg)
def info(msg):      return row("ℹ️ ", msg)
def warn(msg):      return row("⚠️ ", msg)

def result_line(actual, expected, label):
    icon = "✅" if actual == expected else "❌"
    note = "" if actual == expected else f" (erwartet: {expected})"
    return row(icon, f"{label}: total={actual}{note}")

# ── Analyse KI-006: Stale Index nach PUT ──────────────────────────────────────

def analyze_ki006(base, tc):
    IDS = [f"analyze-ki006-{i:03d}" for i in range(1, 5)]

    SINGLE = [("patient", PAT),
              ("mii-provision-provision-code-type", f"{OID}|{OID}.7$permit")]
    AND    = [("patient", PAT),
              ("mii-provision-provision-code-type", f"{OID}|{OID}.7$permit"),
              ("mii-provision-provision-code-type", f"{OID}|{OID}.8$permit")]

    lines = []

    # ── Probe 1: Setup ──
    lines += ["", "## Probe 1 – Setup: 4 Consents (.3.7=permit, .3.8=permit)"]
    cleanup(base, IDS)
    ensure_patient(base)
    for cid in IDS:
        st, _ = fhir_put(base, f"/Consent/{cid}",
                         make_consent(cid, [prov_entry("7", "permit"),
                                            prov_entry("8", "permit")]))
        lines.append(ok(f"PUT {cid}: HTTP {st}") if st in (200, 201)
                     else fail(f"PUT {cid}: HTTP {st}"))
    if any("❌" in l for l in lines):
        cleanup(base, IDS)
        return lines, "FEHLER: Setup fehlgeschlagen – Abbruch."

    # ── Probe 2: Baseline ──
    lines += ["", "## Probe 2 – Baseline-Suche"]
    t_s0, _ = search_total(base, SINGLE)
    t_a0, _ = search_total(base, AND)
    lines.append(result_line(t_s0, 4, "Single .3.7$permit          "))
    lines.append(result_line(t_a0, 4, "AND    .3.7$permit+.3.8$permit"))
    if t_s0 != 4 or t_a0 != 4:
        lines.append(warn("Vorbedingung nicht erfüllt – Custom SP evtl. nicht registriert."))

    # ── Probe 3: Update ──
    lines += ["", "## Probe 3 – PUT Update: Consent-001 .3.7 → deny"]
    st, _ = fhir_put(base, f"/Consent/{IDS[0]}",
                     make_consent(IDS[0], [prov_entry("7", "deny"),
                                           prov_entry("8", "permit")]))
    lines.append(info(f"PUT {IDS[0]} (.3.7→deny): HTTP {st}"))

    # ── Probe 4: Sofortabfrage ──
    lines += ["", "## Probe 4 – Sofort-Abfrage (< 100 ms nach PUT)"]
    t_s_now, _ = search_total(base, SINGLE)
    t_a_now, _ = search_total(base, AND)
    lines.append(result_line(t_s_now, 3, "Single .3.7$permit          "))
    lines.append(result_line(t_a_now, 3, "AND    .3.7$permit+.3.8$permit"))

    # ── Probe 5: Nach 30 s ──
    lines += ["", "## Probe 5 – Abfrage nach 30 s"]
    lines.append(info("Warte 30 s …"))
    time.sleep(30)
    t_s_30, _ = search_total(base, SINGLE)
    t_a_30, _ = search_total(base, AND)
    lines.append(result_line(t_s_30, 3, "Single .3.7$permit          "))
    lines.append(result_line(t_a_30, 3, "AND    .3.7$permit+.3.8$permit"))

    # ── Probe 6: $reindex ──
    lines += ["", "## Probe 6 – POST $reindex, dann Abfrage"]
    st_ri, _ = fhir_post(base, "/$reindex", {
        "resourceType": "Parameters",
        "parameter": [{"name": "resourceType", "valueCode": "Consent"}],
    })
    lines.append(info(f"POST $reindex: HTTP {st_ri}"))
    if st_ri == 200:
        time.sleep(3)
        t_s_ri, _ = search_total(base, SINGLE)
        t_a_ri, _ = search_total(base, AND)
        lines.append(result_line(t_s_ri, 3, "Single nach $reindex        "))
        lines.append(result_line(t_a_ri, 3, "AND    nach $reindex        "))
    else:
        t_s_ri, t_a_ri = None, None
        lines.append(warn("$reindex nicht unterstützt – übersprungen."))

    # ── Schlussfolgerung ──
    lines += ["", "## Schlussfolgerung"]

    single_ok_now  = t_s_now == 3
    and_ok_now     = t_a_now == 3
    single_ok_30   = t_s_30  == 3
    and_ok_30      = t_a_30  == 3
    and_ok_ri      = t_a_ri  == 3 if t_a_ri is not None else None

    if single_ok_now and and_ok_now:
        conclusion = ("**Kein Fehler reproduzierbar.**\n"
                      "Beide Abfragetypen werden sofort korrekt aktualisiert.")
    elif single_ok_now and not and_ok_now:
        if and_ok_30:
            conclusion = ("**KI-006 bestätigt – AND-Query stale (zeitverzögert).**\n\n"
                          "Single-SP-Suche: sofort korrekt ✅\n"
                          "AND-Query: stale nach 0 s, korrekt nach 30 s ✅\n\n"
                          "Ursache: Verzögerter Index-Update für AND-Queries mit "
                          "doppeltem SP-Namen.")
        else:
            ri_note = (f"AND nach $reindex: {t_a_ri}" if and_ok_ri is not None
                       else "$reindex nicht verfügbar")
            conclusion = ("**KI-006 bestätigt – AND-Query persistent stale.**\n\n"
                          "Single-SP-Suche: sofort korrekt ✅\n"
                          "AND-Query: stale nach 0 s und 30 s ❌\n"
                          f"{ri_note}\n\n"
                          "Ursache: Fehler im Index-Update-Pfad für AND-Queries mit "
                          "doppeltem SP-Namen. Cache-Workaround greift nicht.")
    elif not single_ok_now and not and_ok_now:
        if single_ok_30:
            conclusion = ("**KI-006 bestätigt – Single + AND stale (zeitverzögert ~30 s).**\n\n"
                          "Beide Abfragetypen sind nach PUT sofort stale.\n"
                          f"Nach 30 s: Single={'✅' if single_ok_30 else '❌'}, "
                          f"AND={'✅' if and_ok_30 else '❌'}\n\n"
                          "Ursache: Asynchroner Suchindex für Custom Composite SPs.")
        else:
            ri_note = (f"AND nach $reindex: {'✅' if and_ok_ri else '❌ stale'}"
                       if and_ok_ri is not None else "$reindex nicht verfügbar")
            conclusion = ("**KI-006 bestätigt – Single + AND persistent stale (> 30 s).**\n\n"
                          "Beide Abfragetypen sind nach 30 s noch stale.\n"
                          f"{ri_note}\n\n"
                          "Hinweis: Probe verwendet Dual-Provision-Consents (.3.7 + .3.8).\n"
                          "Single-SP-Suche auf Single-Provision-Consents (TC-UPDATE-001-Szenario)\n"
                          "kann separat korrekt funktionieren – prüfbar durch direkten Newman-Lauf.\n\n"
                          "Ursache: Index-Update-Fehler bei Consents mit mehreren Nested-Provisions.")
    else:
        conclusion = "Unerwartetes Ergebnis – manuelle Analyse empfohlen."

    lines.append(conclusion)
    lines.append("\nBekannte Issue: KI-006 (tests/server-specific/known-issues.md)")

    cleanup(base, IDS)
    lines.append("\n_Probe-Consents bereinigt._")
    return lines, conclusion

# ── Analyse KI-002 / KI-005: Nested FHIRPath SP ──────────────────────────────

def analyze_ki002_ki005(base, tc):
    lines = []

    # ── Probe 1: SP registriert? ──
    lines += ["", "## Probe 1 – Custom SearchParameter registriert?"]
    for sp_code in ["mii-provision-provision-code",
                    "mii-provision-provision-code-type"]:
        st, body = fhir_get(base, f"/SearchParameter?code={sp_code}")
        total = body.get("total", 0) if st == 200 else 0
        lines.append(ok(f"{sp_code}: gefunden") if total > 0
                     else fail(f"{sp_code}: NICHT registriert"))
    if any("❌" in l for l in lines):
        return lines, "Custom SPs fehlen – setup.sh ausführen."

    # ── Probe 2: Standard patient-Suche ──
    lines += ["", "## Probe 2 – Standard-Suche ohne Custom SP"]
    t_std, ids_std = search_total(base, [("patient", "Patient/test-patient-001")])
    lines.append(info(f"patient=test-patient-001: total={t_std}, IDs={ids_std}"))

    # ── Probe 3: Suche mit nested SP ──
    lines += ["", "## Probe 3 – Suche mit mii-provision-provision-code (BIOMAT erheben)"]
    BIOMAT_CODE = f"{OID}|{OID}.1"
    t_nested, ids_nested = search_total(
        base, [("patient", "Patient/test-patient-001"),
               ("mii-provision-provision-code", BIOMAT_CODE)])
    lines.append(info(f"mii-provision-provision-code={BIOMAT_CODE}"))
    lines.append(info(f"  total={t_nested}, IDs={ids_nested}"))

    # ── Probe 4: Negativtest mit nicht existentem Code ──
    lines += ["", "## Probe 4 – Negativtest: unbekannter Code (darf 0 Treffer liefern)"]
    FAKE_CODE = f"{OID}|{OID}.999"
    t_fake, _ = search_total(
        base, [("patient", "Patient/test-patient-001"),
               ("mii-provision-provision-code", FAKE_CODE)])
    lines.append(result_line(t_fake, 0, f"mii-provision-provision-code={FAKE_CODE}"))

    # ── Schlussfolgerung ──
    lines += ["", "## Schlussfolgerung"]
    if t_std is None:
        conclusion = "Konnte Basis-Suche nicht auswerten."
    elif t_nested == t_std and t_fake == t_std:
        conclusion = ("**KI-002/005 bestätigt – Nested SP filtert nicht.**\n\n"
                      f"Ohne SP: total={t_std}\n"
                      f"Mit SP (BIOMAT):    total={t_nested} → kein Filtering\n"
                      f"Mit SP (fake Code): total={t_fake}   → kein Filtering\n\n"
                      "Ursache: Server indiziert verschachtelte provision-Elemente "
                      "nicht korrekt.")
    elif t_nested == 0 and (t_std or 0) > 0:
        conclusion = ("**Möglicher Fehler: SP liefert 0 Treffer** – "
                      "evtl. falscher Code oder Fixtures fehlen.")
    elif t_fake == 0:
        conclusion = ("**SP filtert korrekt** (Negativtest bestanden). "
                      "Kein KI-002/005 auf diesem Server.")
    else:
        conclusion = f"Unklares Ergebnis: std={t_std}, nested={t_nested}, fake={t_fake}"

    lines.append(conclusion)
    lines.append("\nBekannte Issues: KI-002, KI-005 (tests/server-specific/known-issues.md)")
    return lines, conclusion

# ── Haupt-Entry-Point ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Root-Cause-Analyse für bekannte FHIR-Testfehler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Beispiele:\n"
            "  python3 scripts/analyze-tc.py --tc TC-UPDATE-003 --server hapi\n"
            "  python3 scripts/analyze-tc.py --ki KI-006 --url http://localhost:8081/fhir\n"
            "  python3 scripts/analyze-tc.py --tc TC-SEARCH-010 --server spark --out report.md\n"
        ))
    parser.add_argument("--tc",     help="Testfall-ID  z.B. TC-UPDATE-003")
    parser.add_argument("--ki",     help="Known-Issue-ID  z.B. KI-006")
    parser.add_argument("--server", choices=SERVERS.keys(),
                        help="Server-Kurzname: hapi | blaze | spark")
    parser.add_argument("--url",    help="FHIR-Base-URL (alternativ zu --server)")
    parser.add_argument("--out",    help="Ausgabedatei (Markdown); Standard: stdout")
    parser.add_argument("--list",   action="store_true",
                        help="Verfügbare Analysen auflisten")
    args = parser.parse_args()

    if args.list:
        print("Verfügbare TCs / KIs:\n")
        for k, v in sorted(TC_TO_ANALYSIS.items()):
            print(f"  {k:<20} → Analyse: {v}")
        return

    target = args.tc or args.ki
    if not target:
        parser.error("Bitte --tc oder --ki angeben (oder --list für Übersicht).")

    if args.url:
        base = args.url.rstrip("/")
    elif args.server:
        base = SERVERS[args.server]
    else:
        parser.error("Bitte --server oder --url angeben.")

    tc_upper = target.upper()
    analysis_key = TC_TO_ANALYSIS.get(tc_upper)
    if not analysis_key:
        print(f"Keine Analyse für '{target}' bekannt.")
        print(f"Tipp: --list zeigt alle verfügbaren Analysen.")
        return

    print(f"Verbinde mit {base} …")
    srv = get_server_info(base)
    print(f"Server: {srv['name']} {srv['version']} (FHIR {srv['fhir']})")
    print(f"Analyse: {tc_upper}\n")

    if analysis_key == "ki006":
        body_lines, conclusion = analyze_ki006(base, tc_upper)
    elif analysis_key == "ki002_ki005":
        body_lines, conclusion = analyze_ki002_ki005(base, tc_upper)
    else:
        body_lines, conclusion = ["Analyse nicht implementiert."], "–"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = [
        f"# Root-Cause-Analyse: {tc_upper}",
        f"",
        f"**Datum:** {now}  ",
        f"**Server:** {srv['name']} {srv['version']} (FHIR {srv['fhir']})  ",
        f"**URL:** {base}  ",
        f"",
        f"---",
    ]
    report = "\n".join(header + body_lines) + "\n"

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(report)
        print(f"\nReport gespeichert: {args.out}")
    else:
        print(report)


if __name__ == "__main__":
    main()
