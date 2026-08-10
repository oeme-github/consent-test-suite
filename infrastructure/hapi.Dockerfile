# Wrappt das offizielle HAPI-FHIR-Image (distroless: keine Shell, kein curl/
# wget) und fügt nur ein statisch gelinktes busybox-Binary hinzu, damit ein
# echter HTTP-Healthcheck (wget --spider) möglich ist. Anwendung, Basis-Image
# und Version bleiben unverändert – reines Hinzufügen einer Datei.
# Die eigentliche HEALTHCHECK-Definition (Intervall, Timeout, Retries) steht
# wie bei blaze/spark in docker-compose.yml, nicht hier.
FROM hapiproject/hapi:v7.4.0

COPY --from=busybox:1.36.1-musl /bin/busybox /bin/busybox
