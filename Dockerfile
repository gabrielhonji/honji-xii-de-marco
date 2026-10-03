FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --system --uid 10001 --create-home app

COPY --chown=app:app server.py ./
COPY --chown=app:app assets/ ./assets/
COPY --chown=app:app web/ ./web/
COPY --chown=app:app documentos-certificados/certificate-background.jpg ./documentos-certificados/certificate-background.jpg

USER app
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3).read()"]

CMD ["python", "server.py", "--host", "0.0.0.0", "--port", "8000", "--public-origin", "https://xii-gabriel.honji.com.br"]
