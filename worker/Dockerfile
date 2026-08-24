# Build stage: install dependencies with build tooling available.
FROM python:3.14-alpine AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage: copy only the installed packages and app code, no build
# tooling, no pip cache, no source of the requirements file.
FROM python:3.14-alpine
WORKDIR /app
RUN addgroup -g 1000 -S app && adduser -u 1000 -S app -G app
COPY --from=builder /root/.local /home/app/.local
COPY worker.py .
ENV PATH=/home/app/.local/bin:$PATH
USER 1000
EXPOSE 80
# Probes 127.0.0.1 rather than localhost because this image resolves
# localhost to ::1 first, and the metrics server's bind '0.0.0.0' is
# IPv4-only (same fix as hasher's Dockerfile).
HEALTHCHECK --interval=15s --timeout=3s CMD ["wget", "-q", "-O-", "http://127.0.0.1:80/healthz"]
CMD ["python", "worker.py"]
