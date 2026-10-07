"""
Rutas WebSocket del módulo de notificaciones.

Este módulo define los endpoints WebSocket relacionados con
las notificaciones en tiempo real.

La ruta:

    /ws/notificaciones/

es atendida por `NotificacionConsumer`, que se encarga de
gestionar la conexión WebSocket del usuario autenticado.

Este archivo únicamente define el enrutamiento.

No contiene:
    - lógica de negocio,
    - autenticación,
    - acceso a la base de datos,
    - publicación de eventos,
    - lógica relacionada con Redis.

Responsabilidad:

    URL WebSocket
        ↓
    NotificacionConsumer
"""

from django.urls import re_path

from apps.notificacion.consumers import NotificacionConsumer


websocket_urlpatterns = [
    re_path(
        r"ws/notificaciones/$",
        NotificacionConsumer.as_asgi(),
    ),
]