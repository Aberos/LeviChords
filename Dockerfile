FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_DEBUG=0 \
    PORT=8000

WORKDIR /app

COPY pyproject.toml README.md ./
COPY apps ./apps
COPY config ./config
COPY manage.py ./

RUN python -m pip install .

RUN DJANGO_SECRET_KEY=collectstatic-only \
    python manage.py collectstatic --noinput

COPY deploy/start.sh ./deploy/start.sh

RUN useradd --create-home --uid 1000 levichords
USER levichords

EXPOSE 8000

CMD ["sh", "deploy/start.sh"]
