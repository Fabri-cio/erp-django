from asgiref.testing import ApplicationCommunicator
from asgiref.sync import async_to_sync

from django.test import TransactionTestCase, override_settings

from rest_framework_simplejwt.tokens import AccessToken

from apps.usuarios.models import Usuario
from config.asgi import application


@override_settings(
    CHANNEL_LAYERS={
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
)
class NotificacionWebSocketTests(TransactionTestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario_ws",
            email="ws@example.com",
            password="password123",
        )

    def crear_token(self):
        return str(
            AccessToken.for_user(self.usuario)
        )

    def ejecutar(self, scope):
        async def test():
            communicator = ApplicationCommunicator(
                application,
                scope,
            )

            await communicator.send_input(
                {
                    "type": "websocket.connect",
                }
            )

            return communicator

        return async_to_sync(test)()

    def test_websocket_con_token_valido_acepta_conexion(self):
        token = self.crear_token()

        scope = {
            "type": "websocket",
            "path": "/ws/notificaciones/",
            "query_string": f"token={token}".encode(),
            "headers": [],
            "subprotocols": [],
        }

        async def test():
            communicator = ApplicationCommunicator(
                application,
                scope,
            )

            await communicator.send_input(
                {
                    "type": "websocket.connect",
                }
            )

            response = await communicator.receive_output(
                timeout=2
            )

            self.assertEqual(
                response["type"],
                "websocket.accept",
            )

            await communicator.send_input(
                {
                    "type": "websocket.disconnect",
                    "code": 1000,
                }
            )

            await communicator.wait()

        async_to_sync(test)()

    def test_websocket_sin_token_cierra_conexion(self):
        scope = {
            "type": "websocket",
            "path": "/ws/notificaciones/",
            "query_string": b"",
            "headers": [],
            "subprotocols": [],
        }

        async def test():
            communicator = ApplicationCommunicator(
                application,
                scope,
            )

            await communicator.send_input(
                {
                    "type": "websocket.connect",
                }
            )

            response = await communicator.receive_output(
                timeout=2
            )

            self.assertEqual(
                response["type"],
                "websocket.close",
            )

            await communicator.wait()

        async_to_sync(test)()