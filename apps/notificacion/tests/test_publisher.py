from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from apps.notificacion.models import Notificacion
from apps.notificacion.publisher import publicar_notificacion


Usuario = get_user_model()


class PublicarNotificacionTests(TransactionTestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario1",
            email="usuario1@test.com",
            password="testpass123",
            is_active=True,
        )

        self.notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="venta.creada",
            titulo="Nueva venta",
            mensaje="Se creó una nueva venta.",
            prioridad=Notificacion.Prioridad.MEDIA,
            entidad_tipo="ventas.venta",
            entidad_id=10,
        )

    # =========================================================
    # PUBLICACIÓN
    # =========================================================

    @patch("apps.notificacion.publisher.get_channel_layer")
    def test_publicar_notificacion_envia_evento(
        self,
        mock_get_channel_layer,
    ):
        channel_layer = AsyncMock()

        mock_get_channel_layer.return_value = channel_layer

        publicar_notificacion(
            self.notificacion,
        )

        channel_layer.group_send.assert_awaited_once()

    # =========================================================
    # GRUPO CORRECTO
    # =========================================================

    @patch("apps.notificacion.publisher.get_channel_layer")
    def test_publicar_notificacion_usa_grupo_del_usuario(
        self,
        mock_get_channel_layer,
    ):
        channel_layer = AsyncMock()

        mock_get_channel_layer.return_value = channel_layer

        publicar_notificacion(
            self.notificacion,
        )

        grupo_esperado = (
            f"notificaciones_usuario_{self.usuario.id}"
        )

        args, kwargs = (
            channel_layer.group_send.call_args
        )

        self.assertEqual(
            args[0],
            grupo_esperado,
        )

        self.assertEqual(
            kwargs,
            {},
        )

    # =========================================================
    # TIPO DEL EVENTO
    # =========================================================

    @patch("apps.notificacion.publisher.get_channel_layer")
    def test_publicar_notificacion_usa_tipo_correcto(
        self,
        mock_get_channel_layer,
    ):
        channel_layer = AsyncMock()

        mock_get_channel_layer.return_value = channel_layer

        publicar_notificacion(
            self.notificacion,
        )

        _, event = (
            channel_layer.group_send.call_args.args
        )

        self.assertEqual(
            event["type"],
            "send_notification",
        )

    # =========================================================
    # DATOS DE LA NOTIFICACIÓN
    # =========================================================

    @patch("apps.notificacion.publisher.get_channel_layer")
    def test_publicar_notificacion_envia_datos_correctos(
        self,
        mock_get_channel_layer,
    ):
        channel_layer = AsyncMock()

        mock_get_channel_layer.return_value = channel_layer

        publicar_notificacion(
            self.notificacion,
        )

        _, event = (
            channel_layer.group_send.call_args.args
        )

        data = event["data"]

        self.assertEqual(
            data["id"],
            self.notificacion.id,
        )

        self.assertEqual(
            data["tipo"],
            self.notificacion.tipo,
        )

        self.assertEqual(
            data["titulo"],
            self.notificacion.titulo,
        )

        self.assertEqual(
            data["mensaje"],
            self.notificacion.mensaje,
        )

        self.assertEqual(
            data["prioridad"],
            self.notificacion.prioridad,
        )

        self.assertEqual(
            data["entidad_tipo"],
            self.notificacion.entidad_tipo,
        )

        self.assertEqual(
            data["entidad_id"],
            self.notificacion.entidad_id,
        )

        self.assertEqual(
            data["leida"],
            self.notificacion.leida,
        )

    # =========================================================
    # FECHA DE CREACIÓN
    # =========================================================

    @patch("apps.notificacion.publisher.get_channel_layer")
    def test_publicar_notificacion_serializa_fecha_creacion(
        self,
        mock_get_channel_layer,
    ):
        channel_layer = AsyncMock()

        mock_get_channel_layer.return_value = channel_layer

        publicar_notificacion(
            self.notificacion,
        )

        _, event = (
            channel_layer.group_send.call_args.args
        )

        fecha_enviada = event["data"]["fecha_creacion"]

        self.assertEqual(
            fecha_enviada,
            self.notificacion.fecha_creacion.isoformat(),
        )

        self.assertIsInstance(
            fecha_enviada,
            str,
        )

    # =========================================================
    # ESTRUCTURA COMPLETA DEL EVENTO
    # =========================================================

    @patch("apps.notificacion.publisher.get_channel_layer")
    def test_publicar_notificacion_estructura_evento_completa(
        self,
        mock_get_channel_layer,
    ):
        channel_layer = AsyncMock()

        mock_get_channel_layer.return_value = channel_layer

        publicar_notificacion(
            self.notificacion,
        )

        _, event = (
            channel_layer.group_send.call_args.args
        )

        self.assertEqual(
            set(event.keys()),
            {
                "type",
                "data",
            },
        )

        self.assertEqual(
            set(event["data"].keys()),
            {
                "id",
                "tipo",
                "titulo",
                "mensaje",
                "prioridad",
                "entidad_tipo",
                "entidad_id",
                "leida",
                "fecha_creacion",
            },
        )