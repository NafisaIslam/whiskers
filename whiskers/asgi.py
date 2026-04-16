"""ASGI entrypoint (unused today but in place if we add channels/async views)."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whiskers.settings")

application = get_asgi_application()
