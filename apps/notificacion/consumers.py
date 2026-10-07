import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificacionConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket encargado de entregar notificaciones
    en tiempo real al usuario autenticado.

    Responsabilidades:
        - Validar que exista un usuario autenticado.
        - Asociar la conexión a un grupo privado del usuario.
        - Aceptar la conexión WebSocket.
        - Escuchar eventos de notificación enviados al grupo.
        - Enviar la información de la notificación al cliente.
        - Retirar la conexión del grupo al desconectarse.

    Este consumer se encarga únicamente del transporte en tiempo real.

    No contiene lógica de negocio ni crea notificaciones.
    La persistencia de las notificaciones pertenece al módulo
    `apps.notificacion.services`, mientras que este consumer
    se limita a entregar eventos mediante WebSocket.

    Cada usuario tiene un grupo privado con el formato:

        notificaciones_usuario_<id>

    De esta manera, una notificación enviada a un usuario
    no se transmite a otros usuarios conectados.
    """

    async def connect(self):
        """
        Acepta una conexión WebSocket de un usuario autenticado.

        El usuario es obtenido desde `scope["user"]`, previamente
        establecido por el middleware de autenticación WebSocket.

        Si no existe un usuario autenticado, la conexión se cierra
        inmediatamente con el código 4001.

        Una vez autenticado, el canal se agrega al grupo privado
        correspondiente al usuario y se acepta la conexión.
        """

        usuario = self.scope.get("user")

        if usuario is None or not usuario.is_authenticated:
            await self.close(code=4001)
            return

        self.usuario_id = usuario.id

        self.group_name = (
            f"notificaciones_usuario_{self.usuario_id}"
        )

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Retira la conexión del grupo privado del usuario.

        Este método se ejecuta cuando el cliente cierra la conexión
        o cuando la conexión termina por cualquier otra razón.

        El grupo se elimina únicamente si fue creado durante
        el proceso de conexión.
        """

        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name,
            )

    async def receive(self, text_data):
        """
        Procesa mensajes enviados por el cliente.

        Actualmente el servidor no necesita recibir mensajes del
        cliente mediante WebSocket.

        Las acciones sobre las notificaciones, como marcar una
        notificación como leída, se realizan mediante la API REST.

        El WebSocket se utiliza únicamente para entregar eventos
        en tiempo real al cliente.
        """

        pass

    async def send_notification(self, event):
        """
        Envía una notificación al cliente conectado.

        Este método es invocado automáticamente por Django Channels
        cuando se publica un evento en el grupo del usuario cuyo
        tipo es `send_notification`.

        El contenido de `event["data"]` corresponde a la información
        serializada de la notificación y se envía al cliente como
        JSON.

        Args:
            event:
                Diccionario generado por `group_send()` que contiene
                los datos de la notificación.
        """

        await self.send(
            text_data=json.dumps(event["data"])
        )