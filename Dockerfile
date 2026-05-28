# syntax=docker/dockerfile:1
FROM python:3.12-slim

# ── Security: run as a non-root user ───────────────────────────────────────
RUN addgroup --system appuser \
 && adduser --system --ingroup appuser --home /app --no-create-home appuser

WORKDIR /app

# ── Dependencies ────────────────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application source ──────────────────────────────────────────────────────
COPY app/ ./app/

# Give appuser ownership of the working directory (gunicorn writes a control
# socket here and will log a harmless error if the directory is not writable).
RUN chown -R appuser:appuser /app

# ── Runtime ─────────────────────────────────────────────────────────────────
USER appuser
EXPOSE 8080

# Gunicorn: 2 workers is plenty for an I/O-bound proxy.
# Tune WEB_CONCURRENCY via an env var if needed.
ENV WEB_CONCURRENCY=2

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["gunicorn", \
     "--bind", "0.0.0.0:8080", \
     "--workers", "2", \
     "--timeout", "60", \
     "--pid", "/tmp/gunicorn.pid", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app.main:app"]
