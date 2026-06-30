# Test-Design-Grundsätze

Regeln und Erkenntnisse aus der Arbeit mit dieser Test-Suite.
Entstanden aus konkreten Erfahrungen — nicht abstrakt, sondern aus Fehlern gelernt.

---

## 1. Server-Dokumentation lesen, bevor ein Failure als Bug klassifiziert wird

**Regel:** Vor jedem Upstream-Issue-Report die Dokumentation des betroffenen Servers
auf bekannte Einschränkungen oder Konfigurationsvoraussetzungen prüfen.

**Hintergrund (Spark, 2026-06-30):**
Spark unterscheidet zwei Indexierungs-Modi:
- `Synchronous` (Standard): Index wird synchron im HTTP-Request-Pfad aktualisiert
- `Background` (experimentell): Index wird asynchron über eine MongoDB `indexqueue` aktualisiert

Im `Background`-Modus sind Suchergebnisse *eventually consistent* — ein Test, der
direkt nach einem `PUT` sucht, kann vorübergehend Stale Results sehen. Das wäre kein
Bug, sondern dokumentiertes Verhalten.

Unser Setup verwendet den Standard (`Synchronous`), daher ist Stale Index nach `PUT`
ein echter Bug (→ FirelyTeam/spark#1319). Hätten wir im Hintergrundmodus getestet,
wäre das Ergebnis dasselbe, aber die Ursache eine andere.

**Checkliste vor Upstream-Report:**
- [ ] Server-Doku auf bekannte Limitations geprüft?
- [ ] Konfigurationsmodus verifiziert (nicht nur Default angenommen)?
- [ ] Bereits bekannte / geschlossene Issues zum Thema gesucht?

---

## 2. Indexierungs-Modus des Servers verifizieren

**Regel:** Bei Stale-Index-Verdacht immer prüfen welcher Indexierungs-Modus aktiv ist,
bevor ein Fehler klassifiziert wird.

**Für Spark:** Presence der `indexqueue`-Collection in MongoDB zeigt Background-Modus:
```bash
docker exec consent-test-spark-mongo mongosh spark --eval "db.getCollectionNames()" --quiet
# Enthält 'indexqueue' → Background-Modus aktiv → eventually consistent
# Kein 'indexqueue'   → Synchronous-Modus → Stale Index ist ein Bug
```

**Implikation für unsere Tests:**
Alle TC-UPDATE-Tests setzen `Synchronous`-Indexierung voraus. Sie prüfen direkt nach
`PUT` ob der Suchindex aktualisiert ist. Das ist nur berechtigt im Synchronous-Modus.
Wer diese Tests im Background-Modus ausführt, muss Retry-Logik ergänzen oder den
Modus auf `Synchronous` zurückstellen.

---

## 3. SearchParameter-Registrierung ist serverabhängig

**Regel:** Nie davon ausgehen, dass `PUT /SearchParameter/<id>` auf allen Servern
wirksam ist.

**Erfahrung (Blaze, 2026-06-30):**
Blaze ignoriert SearchParameter-Ressourcen, die per REST registriert werden.
Custom SPs müssen über eine gemountete Bundle-Datei beim Start eingebunden werden:
```yaml
environment:
  DB_SEARCH_PARAM_BUNDLE: "/app/blaze-sp-bundle.json"
volumes:
  - ./blaze-sp-bundle.json:/app/blaze-sp-bundle.json:ro
```

Symptom wenn dieser Schritt fehlt: Der Server akzeptiert den PUT (HTTP 201), wendet
den SP aber beim Suchen nicht an — Over-Matching oder Zero-Matching als Ergebnis.
Das sieht wie ein Bug aus, ist aber ein Konfigurationsfehler.

**Server-Übersicht (Stand 2026-06-30):**
| Server | SP-Registrierung | Methode |
|---|---|---|
| HAPI v7.4.0 | REST PUT `SearchParameter/<id>` | asynchron, vor Fixtures laden |
| Blaze 1.9.0 | Datei-Mount `DB_SEARCH_PARAM_BUNDLE` | beim Container-Start |
| Spark r4-latest | REST PUT `SearchParameter/<id>` | synchron |

---

## 4. Setup-Reihenfolge: SearchParameter vor Fixtures

**Regel:** SearchParameter müssen immer vor Fixtures geladen werden.

**Hintergrund (HAPI):**
HAPI verarbeitet neu registrierte Custom SPs asynchron. Ressourcen, die **vor**
der SP-Registrierung geladen wurden, werden nicht automatisch reindiziert.
Da `setup.sh` SPs vor Fixtures lädt, sind alle Consents sofort korrekt indexiert.

Manuelles Abweichen von dieser Reihenfolge (z.B. interaktives Testen) erfordert
anschließend `POST /$reindex` für den betroffenen Ressourcentyp.

---

## 5. Tests zeigen Bugs — sie verstecken sie nicht

**Regel:** Bekannte Server-Bugs bleiben als Failures sichtbar. Kein `xfail`, kein
Tolerieren falscher Ergebnisse per `at.least()` (außer explizit begründet in
`known-issues.md`).

**Begründung:**
Der Zweck dieser Test-Suite ist es, anderen Teams zu zeigen ob ein Server das
MII Consent-Suchmodell korrekt implementiert. Ein Test der einen Bug verbirgt
erzeugt falsches Vertrauen und verfehlt diesen Zweck.

Ausnahme: Wenn ein FHIR-Server per Spezifikation mehrere korrekte Antworten
erlaubt (z.B. Over-Inclusion ist laut FHIR-Spec zulässig), wird das in
`known-issues.md` erklärt und der Test entsprechend formuliert.
