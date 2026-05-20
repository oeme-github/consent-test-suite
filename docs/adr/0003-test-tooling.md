# ADR-0003: Test-Tooling (FHIR TestScript + Newman)

## Status
Akzeptiert

## Kontext

Zwei Anforderungen an das Test-Tooling stehen in Spannung:

1. **HL7-Kompatibilität**: Tests sollen als FHIR TestScript-Ressourcen
   ausgedrückt werden können, damit sie mit der Community geteilt und
   auf Touchstone ausgeführt werden können.

2. **CI-Fähigkeit**: Tests müssen in GitHub Actions ohne manuelle
   Interaktion laufen und strukturierte Reports erzeugen.

## Entscheidung

**Zweigleisiger Ansatz:**

| Ebene | Tool | Zweck |
|---|---|---|
| Canonical | FHIR TestScript (JSON) | HL7-Standard, Dokumentation, Touchstone |
| CI-Ausführung | Newman (Postman CLI) | Automatisierung, Reports, GitHub Actions |

FHIR TestScripts werden als **Quelle der Wahrheit** gepflegt. Für die
CI-Pipeline werden sie in Postman Collections konvertiert (Skript in
`infrastructure/convert-testscript.sh`).

**Für komplexe Logik** (z.B. mehrstufige Prozess-Tests) kann
ergänzend **pytest + fhir.resources** eingesetzt werden.

## Konsequenzen

**Positiv:**
- Tests sind auf Touchstone direkt ausführbar → Community-Akzeptanz
- Newman erzeugt JUnit-kompatible XML-Reports für GitHub Actions
- Kein proprietäres Tool-Lock-in

**Negativ / Einschränkungen:**
- Konvertierungsschritt TestScript → Newman muss gepflegt werden
- TestScript-Ausdrucksmöglichkeiten sind begrenzt (FHIRPath-Assertions)

## Alternativen verworfen

- **Nur Touchstone**: Kein natives CI/CD, manuelle Ausführung
- **Nur pytest**: Kein HL7-Standard, schlechte Community-Teilbarkeit
- **Inferno**: Zu generisch, kein Consent-spezifischer Support
