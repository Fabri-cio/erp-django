from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.notificacion.models import Notificacion
from apps.notificacion.serializers import NotificacionSerializer

Usuario = get_user_model()


class NotificacionSerializerTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario1",
            email="usuario1@test.com",
            password="testpass123",
        )

        self.notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="venta.creada",
            titulo="Nueva venta",
            mensaje="Se creó una nueva venta.",
            prioridad=Notificacion.Prioridad.ALTA,
            entidad_tipo="ventas.venta",
            entidad_id=123,
        )

    # =========================================================
    # SERIALIZACIÓN
    # =========================================================

    def test_serializa_notificacion(self):
        serializer = NotificacionSerializer(
            instance=self.notificacion,
        )

        data = serializer.data

        self.assertEqual(
            data["id"],
            self.notificacion.id,
        )
        self.assertEqual(
            data["tipo"],
            "venta.creada",
        )
        self.assertEqual(
            data["titulo"],
            "Nueva venta",
        )
        self.assertEqual(
            data["mensaje"],
            "Se creó una nueva venta.",
        )
        self.assertEqual(
            data["prioridad"],
            Notificacion.Prioridad.ALTA,
        )
        self.assertEqual(
            data["entidad_tipo"],
            "ventas.venta",
        )
        self.assertEqual(
            data["entidad_id"],
            123,
        )
        self.assertFalse(
            data["leida"],
        )
        self.assertIsNotNone(
            data["fecha_creacion"],
        )
        self.assertIsNone(
            data["fecha_lectura"],
        )

    # =========================================================
    # CAMPOS
    # =========================================================

    def test_expone_exactamente_los_campos_definidos(self):
        serializer = NotificacionSerializer(
            instance=self.notificacion,
        )

        self.assertEqual(
            set(serializer.data.keys()),
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
                "fecha_lectura",
            },
        )

    # =========================================================
    # SOLO LECTURA
    # =========================================================

    def test_todos_los_campos_son_read_only(self):
        serializer = NotificacionSerializer()

        for field_name, field in serializer.fields.items():
            self.assertTrue(
                field.read_only,
                msg=f"El campo '{field_name}' debería ser read_only.",
            )

    # =========================================================
    # NO PERMITE CREACIÓN
    # =========================================================

    def test_no_acepta_datos_de_entrada_para_crear(self):
        data = {
            "tipo": "venta.creada",
            "titulo": "Nueva venta",
            "mensaje": "Mensaje",
            "prioridad": Notificacion.Prioridad.ALTA,
            "entidad_tipo": "ventas.venta",
            "entidad_id": 123,
            "leida": False,
        }

        serializer = NotificacionSerializer(
            data=data,
        )

        self.assertTrue(
            serializer.is_valid(),
        )

        self.assertEqual(
            serializer.validated_data,
            {},
        )

    # =========================================================
    # FECHA DE LECTURA
    # =========================================================

    def test_serializa_fecha_de_lectura(self):
        fecha_lectura = timezone.now()

        self.notificacion.leida = True
        self.notificacion.fecha_lectura = fecha_lectura
        self.notificacion.save()

        self.notificacion.refresh_from_db()

        serializer = NotificacionSerializer(
            instance=self.notificacion,
        )

        self.assertIsNotNone(
            serializer.data["fecha_lectura"],
        )

    # =========================================================
    # NO INCLUYE USUARIO
    # =========================================================

    def test_no_expone_usuario(self):
        serializer = NotificacionSerializer(
            instance=self.notificacion,
        )

        self.assertNotIn(
            "usuario",
            serializer.data,
        )