import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Ensure Django apps are loaded before importing modules that touch models/auth
django.setup()

django_asgi_app = get_asgi_application()

# Import after setup to avoid AppRegistryNotReady
from apps.tracker.routing import websocket_urlpatterns
from apps.tracker.middlewares import JWTAuthMiddlewareStack  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)