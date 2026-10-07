from rest_framework import serializers

from apps.notificacion.models import Notificacion


class NotificacionSerializer(serializers.ModelSerializer):
    """
    Serializer de lectura para las notificaciones del usuario autenticado.

    Este serializer no permite crear ni modificar notificaciones desde
    la API de forma directa. La creación debe realizarse mediante
    `apps.notificacion.services`.

    Los cambios de estado, como marcar una notificación como leída,
    se realizan mediante endpoints específicos.
    """

    class Meta:
        model = Notificacion

        fields = [
            "id",
            "tipo",
            "titulo",
            "mensaje",
            "prioridad",
            "entidad_tipo",
            "entidad_id",
            "leida",
            "fecha_creacion",
            "fecha_lectura",
        ]

        # Todos los campos son controlados por el backend.
        # El frontend únicamente los recibe.
        read_only_fields = fields