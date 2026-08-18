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
HEALTHCHECK --interval=15s --timeout=3s CMD ["pgrep", "-f", "worker.py"]
CMD ["python", "worker.py"]
