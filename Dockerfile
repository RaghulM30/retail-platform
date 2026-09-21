FROM python:3.12-slim

WORKDIR /app

COPY app/app.py .

ENV APP_VERSION=4.2.2
ENV APP_ENV=production

RUN useradd -m appuser && chown -R appuser /app

USER appuser

EXPOSE 8081

HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9999/payment')"

CMD ["python", "app.py"]