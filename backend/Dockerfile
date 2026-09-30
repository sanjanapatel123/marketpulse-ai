FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system marketpulse \
    && adduser \
        --system \
        --ingroup marketpulse \
        marketpulse

COPY requirements.txt .

RUN pip install \
    --upgrade pip \
    && pip install \
        --requirement requirements.txt

COPY app ./app
COPY scripts ./scripts
COPY pytest.ini ./

RUN chown -R marketpulse:marketpulse /app

USER marketpulse

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]