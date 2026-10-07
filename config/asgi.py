"""
Configuración de la aplicación ASGI del proyecto.

Este módulo define cómo Django y Django Channels reciben y
procesan las conexiones HTTP y WebSocket.

El proyecto utiliza una única aplicación ASGI para ambos tipos
de comunicación:

    HTTP
        ↓
    Django ASGI
        ↓
    API REST

    WebSocket
        ↓
    JWTAuthMiddleware
        ↓
    URLRouter
        ↓
    NotificacionConsumer

La autenticación JWT del WebSocket se realiza mediante el
middleware propio del módulo de notificaciones.

Este archivo únicamente configura el enrutamiento de protocolos.
No contiene lógica de negocio.
"""

import os


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)


from django.core.asgi import get_asgi_application


django_asgi_app = get_asgi_application()


from channels.routing import ProtocolTypeRouter, URLRouter

from apps.notificacion.middleware import JWTAuthMiddleware
from apps.notificacion.routing import websocket_urlpatterns


application = ProtocolTypeRouter(
    {
        # Todas las peticiones HTTP continúan utilizando
        # la aplicación ASGI estándar de Django.
        "http": django_asgi_app,

        # Las conexiones WebSocket pasan primero por el
        # middleware de autenticación JWT y posteriormente
        # por las rutas WebSocket del proyecto.
        "websocket": JWTAuthMiddleware(
            URLRouter(websocket_urlpatterns),
        ),
    }
)