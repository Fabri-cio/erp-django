from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from apps.notificacion.models import Notificacion

Usuario = get_user_model()


class NotificacionModelTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario1",
            email="usuario1@test.com",
            password="testpass123",
        )

    # =========================================================
    # CREACIÓN
    # =========================================================

    def test_crear_notificacion(self):
        notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="venta.creada",
            titulo="Nueva venta",
            mensaje="Se creó una nueva venta.",
        )

        self.assertIsNotNone(notificacion.id)
        self.assertEqual(notificacion.usuario, self.usuario)
        self.assertEqual(notificacion.tipo, "venta.creada")
        self.assertEqual(notificacion.titulo, "Nueva venta")
        self.assertEqual(
            notificacion.mensaje,
            "Se creó una nueva venta.",
        )

    # =========================================================
    # VALORES POR DEFECTO
    # =========================================================

    def test_valores_por_defecto(self):
        notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="venta.creada",
            titulo="Nueva venta",
            mensaje="Se creó una nueva venta.",
        )

        self.assertEqual(
            notificacion.prioridad,
            Notificacion.Prioridad.MEDIA,
        )

        self.assertFalse(
            notificacion.leida,
        )

        self.assertEqual(
            notificacion.entidad_tipo,
            "",
        )

        self.assertIsNone(
            notificacion.entidad_id,
        )

        self.assertIsNone(
            notificacion.fecha_lectura,
        )

    # =========================================================
    # PRIORIDAD
    # =========================================================

    def test_prioridades_disponibles(self):
        self.assertEqual(
            Notificacion.Prioridad.BAJA,
            "baja",
        )

        self.assertEqual(
            Notificacion.Prioridad.MEDIA,
            "media",
        )

        self.assertEqual(
            Notificacion.Prioridad.ALTA,
            "alta",
        )

    def test_puede_guardar_diferentes_prioridades(self):
        for prioridad in Notificacion.Prioridad.values:
            notificacion = Notificacion.objects.create(
                usuario=self.usuario,
                tipo="prueba",
                titulo=f"Prioridad {prioridad}",
                mensaje="Mensaje",
                prioridad=prioridad,
            )

            self.assertEqual(
                notificacion.prioridad,
                prioridad,
            )

    # =========================================================
    # ESTADO DE LECTURA
    # =========================================================

    def test_marcar_como_leida(self):
        notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación",
            mensaje="Mensaje",
        )

        fecha = timezone.now()

        notificacion.leida = True
        notificacion.fecha_lectura = fecha
        notificacion.save()

        notificacion.refresh_from_db()

        self.assertTrue(
            notificacion.leida,
        )

        self.assertIsNotNone(
            notificacion.fecha_lectura,
        )

    # =========================================================
    # ENTIDAD RELACIONADA
    # =========================================================

    def test_puede_guardar_referencia_a_entidad(self):
        notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="venta.creada",
            titulo="Nueva venta",
            mensaje="Se creó una nueva venta.",
            entidad_tipo="ventas.venta",
            entidad_id=123,
        )

        self.assertEqual(
            notificacion.entidad_tipo,
            "ventas.venta",
        )

        self.assertEqual(
            notificacion.entidad_id,
            123,
        )

    # =========================================================
    # FECHA DE CREACIÓN
    # =========================================================

    def test_fecha_creacion_se_genera_automaticamente(self):
        notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación",
            mensaje="Mensaje",
        )

        self.assertIsNotNone(
            notificacion.fecha_creacion,
        )

    # =========================================================
    # REPRESENTACIÓN
    # =========================================================

    def test_str(self):
        notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Nueva venta",
            mensaje="Mensaje",
        )

        self.assertEqual(
            str(notificacion),
            "Nueva venta - usuario1",
        )

    # =========================================================
    # RELACIÓN CON USUARIO
    # =========================================================

    def test_usuario_puede_tener_varias_notificaciones(self):
        Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación 1",
            mensaje="Mensaje",
        )

        Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación 2",
            mensaje="Mensaje",
        )

        self.assertEqual(
            self.usuario.notificaciones.count(),
            2,
        )

    # =========================================================
    # PROTECCIÓN DEL USUARIO
    # =========================================================

    def test_usuario_no_puede_eliminarse_si_tiene_notificaciones(self):
        Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación",
            mensaje="Mensaje",
        )

        with self.assertRaises(IntegrityError):
            self.usuario.delete()

    # =========================================================
    # ORDENAMIENTO
    # =========================================================

    def test_notificaciones_se_ordenan_por_fecha_descendente(self):
        primera = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Primera",
            mensaje="Mensaje",
        )

        segunda = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Segunda",
            mensaje="Mensaje",
        )

        notificaciones = list(
            Notificacion.objects.all()
        )

        self.assertEqual(
            notificaciones[0].id,
            segunda.id,
        )

        self.assertEqual(
            notificaciones[1].id,
            primera.id,
        )