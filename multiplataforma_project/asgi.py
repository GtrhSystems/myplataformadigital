"""
ASGI config for multiplataforma_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""



import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import django
django.setup()
import multiplataforma.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'multiplataforma_project.settings')
application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            multiplataforma.routing.websocket_urlpatterns
        )
    ),
})