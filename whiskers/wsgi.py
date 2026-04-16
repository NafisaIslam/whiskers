"""WSGI entrypoint for production servers (gunicorn)."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whiskers.settings")

application = get_wsgi_application()
