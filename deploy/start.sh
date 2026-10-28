#!/bin/sh
set -e

python manage.py migrate --noinput

if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    python manage.py createsuperuser --noinput || true
fi

exec gunicorn config.wsgi --bind "0.0.0.0:${PORT}" --access-logfile -
