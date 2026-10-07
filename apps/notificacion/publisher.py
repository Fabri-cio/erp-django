from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def publicar_notificacion(notificacion):
    """
    Publica una notificación en tiempo real mediante WebSocket.

    Esta función no crea ni modifica la notificación en la base
    de datos. Su única responsabilidad es enviar el evento al
    canal privado del usuario correspondiente.

    Flujo:

        Notificación guardada
                ↓
        publicar_notificacion()
                ↓
        grupo privado del usuario
                ↓
        NotificacionConsumer
                ↓
        WebSocket
                ↓
        Frontend

    El grupo tiene el formato:

        notificaciones_usuario_<usuario_id>

    De esta manera, la notificación solamente se envía al usuario
    propietario de la notificación.

    Args:
        notificacion:
            Instancia de `Notificacion` que ya debe existir
            en la base de datos.
    """

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"notificaciones_usuario_{notificacion.usuario_id}",
        {
            "type": "send_notification",
            "data": {
                "id": notificacion.id,
                "tipo": notificacion.tipo,
                "titulo": notificacion.titulo,
                "mensaje": notificacion.mensaje,
                "prioridad": notificacion.prioridad,
                "entidad_tipo": notificacion.entidad_tipo,
                "entidad_id": notificacion.entidad_id,
                "leida": notificacion.leida,
                "fecha_creacion": (
                    notificacion.fecha_creacion.isoformat()
                ),
            },
        },
    )