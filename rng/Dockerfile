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
COPY rng.py .
# FLASK_RUN_HOST=:: binds both IPv4 and IPv6, since the compose healthcheck
# probes over IPv4 while Kubernetes probes may use either.
ENV PATH=/home/app/.local/bin:$PATH \
    FLASK_APP=rng \
    FLASK_RUN_HOST=:: \
    FLASK_RUN_PORT=80
USER 1000
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s CMD ["wget", "-q", "-O-", "http://localhost:80/healthz"]
CMD ["python", "-m", "flask", "run", "--without-threads"]
