# Upstream Issue Watch

Offene Issues bei externen Projekten, die aus diesem Repo gemeldet wurden.
Wird bei jedem Session-Start geprüft (siehe CLAUDE.md).

---

## KI-006: Stale Suchindex nach PUT (Multi-Provision Consents)

**hapifhir/hapi-fhir#8104**
URL: https://github.com/hapifhir/hapi-fhir/issues/8104
Gemeldet: 2026-06-18
Letzter Stand: 0 Kommentare (2026-06-18T14:27:15Z)

---

## KI-002: Nested FHIRPath in Custom SearchParameter (Over-Matching)

**samply/blaze#3716**
URL: https://github.com/samply/blaze/issues/3716
Gemeldet: 2026-06-18
Letzter Stand: 3 Kommentare (2026-06-30T10:59:56Z)

**Kommentar von alexanderkiel (2026-06-29):**
> Hi, can you please point me to the 5 example Consent resources you used here?

→ Geantwortet (2026-06-29): Links zu allen 5 Fixtures und SearchParameter-Definitionen gepostet.
Kommentar: https://github.com/samply/blaze/issues/3716#issuecomment-4833572972

**Antwort von alexanderkiel (2026-06-30):**
> Do you have mounted a file with the MII search parameters as described
> [here](https://blaze-server.org/deployment/environment-variables.html#db-search-param-bundle)?
> Just creating a SearchParameter resource doesn't work.
> Works for me. It returns only 4 Consent resources.

→ **KI-002 ist vermutlich kein Blaze-Bug!** Blaze erfordert SP-Registrierung über
  gemountete Datei (`DB_SEARCH_PARAM_BUNDLE`), nicht per REST-POST. Unser Setup
  postet SearchParameter als FHIR-Ressourcen — das wird ignoriert.
  Nächster Schritt: docker-compose.yml und setup.sh für Blaze auf SP-Bundle-Mount
  umstellen (D01). KI-002 nach Fix schließen oder neu klassifizieren.

---

## KI-003: Composite SearchParameter Over-Matching bei provisionCodePeriod

**hapifhir/hapi-fhir#8126**
URL: https://github.com/hapifhir/hapi-fhir/issues/8126
Gemeldet: 2026-06-29
Letzter Stand: 0 Kommentare (2026-06-29)
