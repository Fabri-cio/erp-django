from asgiref.sync import async_to_sync

from unittest.mock import AsyncMock

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from apps.notificacion.consumers import NotificacionConsumer


Usuario = get_user_model()


class NotificacionConsumerTests(TransactionTestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario1",
            email="usuario1@test.com",
            password="testpass123",
            is_active=True,
        )

    # =========================================================
    # HELPER
    # =========================================================

    def crear_consumer(self, usuario=None):
        consumer = NotificacionConsumer()

        consumer.scope = {
            "type": "websocket",
            "user": usuario,
        }

        consumer.channel_layer = AsyncMock()
        consumer.channel_name = "test_channel"

        consumer.accept = AsyncMock()
        consumer.close = AsyncMock()
        consumer.send = AsyncMock()

        return consumer

    # =========================================================
    # CONEXIÓN AUTENTICADA
    # =========================================================

    def test_usuario_autenticado_acepta_conexion(self):
        consumer = self.crear_consumer(
            self.usuario,
        )

        async_to_sync(
            consumer.connect
        )()

        consumer.accept.assert_awaited_once()

        consumer.close.assert_not_awaited()

    # =========================================================
    # GRUPO DEL USUARIO
    # =========================================================

    def test_usuario_autenticado_se_agrega_al_grupo_correcto(self):
        consumer = self.crear_consumer(
            self.usuario,
        )

        async_to_sync(
            consumer.connect
        )()

        nombre_grupo = (
            f"notificaciones_usuario_{self.usuario.id}"
        )

        consumer.channel_layer.group_add.assert_awaited_once_with(
            nombre_grupo,
            consumer.channel_name,
        )

    # =========================================================
    # INFORMACIÓN DEL CONSUMER
    # =========================================================

    def test_usuario_autenticado_guarda_usuario_id_y_group_name(self):
        consumer = self.crear_consumer(
            self.usuario,
        )

        async_to_sync(
            consumer.connect
        )()

        self.assertEqual(
            consumer.usuario_id,
            self.usuario.id,
        )

        self.assertEqual(
            consumer.group_name,
            f"notificaciones_usuario_{self.usuario.id}",
        )

    # =========================================================
    # USUARIO NO AUTENTICADO
    # =========================================================

    def test_usuario_no_autenticado_rechaza_conexion(self):
        consumer = self.crear_consumer(
            None,
        )

        async_to_sync(
            consumer.connect
        )()

        consumer.close.assert_awaited_once_with(
            code=4001,
        )

        consumer.accept.assert_not_awaited()

        consumer.channel_layer.group_add.assert_not_awaited()

    # =========================================================
    # DESCONEXIÓN
    # =========================================================

    def test_disconnect_sale_del_grupo(self):
        consumer = self.crear_consumer(
            self.usuario,
        )

        async_to_sync(
            consumer.connect
        )()

        consumer.channel_layer.group_discard.reset_mock()

        async_to_sync(
            consumer.disconnect
        )(1000)

        consumer.channel_layer.group_discard.assert_awaited_once_with(
            consumer.group_name,
            consumer.channel_name,
        )

    # =========================================================
    # RECEIVE
    # =========================================================

    def test_receive_no_hace_nada(self):
        consumer = self.crear_consumer(
            self.usuario,
        )

        async_to_sync(
            consumer.receive
        )(
            '{"mensaje": "hola"}',
        )

        consumer.send.assert_not_awaited()

    # =========================================================
    # ENVÍO DE NOTIFICACIÓN
    # =========================================================

    def test_send_notification_envia_json(self):
        consumer = self.crear_consumer(
            self.usuario,
        )

        data = {
            "id": 1,
            "tipo": "venta.creada",
            "titulo": "Nueva venta",
            "mensaje": "Se creó una nueva venta.",
            "prioridad": "media",
            "entidad_tipo": "ventas.venta",
            "entidad_id": 10,
            "leida": False,
            "fecha_creacion": "2026-10-01T20:00:00+00:00",
        }

        event = {
            "type": "send_notification",
            "data": data,
        }

        async_to_sync(
            consumer.send_notification
        )(event)

        consumer.send.assert_awaited_once_with(
            text_data=__import__("json").dumps(data),
        )