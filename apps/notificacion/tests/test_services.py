from django.contrib.auth import get_user_model
from django.test import TestCase

from django.utils import timezone

from apps.notificacion.models import Notificacion
from apps.notificacion.services import (
    crear_notificacion,
    crear_notificaciones,
    marcar_como_leida,
    marcar_todas_como_leidas,
    contar_no_leidas,
)


Usuario = get_user_model()


class CrearNotificacionTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario_test",
            email="usuario@test.com",
            password="TestPassword123",
        )

    def test_crear_notificacion(self):
        notificacion = crear_notificacion(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación de prueba",
            mensaje="Mensaje de prueba",
        )

        self.assertIsNotNone(notificacion.id)

        self.assertEqual(
            notificacion.usuario,
            self.usuario,
        )

        self.assertEqual(
            notificacion.tipo,
            "prueba",
        )

        self.assertEqual(
            notificacion.titulo,
            "Notificación de prueba",
        )

        self.assertEqual(
            notificacion.mensaje,
            "Mensaje de prueba",
        )

        self.assertEqual(
            notificacion.prioridad,
            Notificacion.Prioridad.MEDIA,
        )

        self.assertFalse(notificacion.leida)

        self.assertEqual(
            Notificacion.objects.count(),
            1,
        )

    def test_crear_notificacion_con_entidad(self):
        entidad = Usuario.objects.create_user(
            username="entidad_test",
            email="entidad@test.com",
            password="TestPassword123",
        )

        notificacion = crear_notificacion(
            usuario=self.usuario,
            tipo="prueba.entidad",
            titulo="Notificación con entidad",
            mensaje="Mensaje asociado a una entidad.",
            entidad=entidad,
        )

        self.assertEqual(
            notificacion.entidad_tipo,
            "usuarios.usuario",
        )

        self.assertEqual(
            notificacion.entidad_id,
            entidad.id,
        )

    def test_crear_notificacion_con_entidad_no_guardada(self):
        entidad = Usuario(
            username="entidad_no_guardada",
            email="entidad_no_guardada@test.com",
        )

        with self.assertRaises(ValueError):
            crear_notificacion(
                usuario=self.usuario,
                tipo="prueba.entidad",
                titulo="Notificación",
                mensaje="Mensaje",
                entidad=entidad,
            )


class CrearNotificacionesTests(TestCase):

    def setUp(self):
        self.usuario_1 = Usuario.objects.create_user(
            username="usuario_1",
            email="usuario1@test.com",
            password="TestPassword123",
        )

        self.usuario_2 = Usuario.objects.create_user(
            username="usuario_2",
            email="usuario2@test.com",
            password="TestPassword123",
        )

    def test_crear_notificaciones_para_varios_usuarios(self):
        notificaciones = crear_notificaciones(
            usuarios=[
                self.usuario_1,
                self.usuario_2,
            ],
            tipo="prueba.multiple",
            titulo="Notificación múltiple",
            mensaje="Mensaje para varios usuarios.",
            prioridad=Notificacion.Prioridad.ALTA,
        )

        self.assertEqual(
            len(notificaciones),
            2,
        )

        self.assertEqual(
            Notificacion.objects.count(),
            2,
        )

        self.assertEqual(
            notificaciones[0].usuario,
            self.usuario_1,
        )

        self.assertEqual(
            notificaciones[1].usuario,
            self.usuario_2,
        )

        self.assertEqual(
            notificaciones[0].tipo,
            "prueba.multiple",
        )

        self.assertEqual(
            notificaciones[0].titulo,
            "Notificación múltiple",
        )

        self.assertEqual(
            notificaciones[0].mensaje,
            "Mensaje para varios usuarios.",
        )

        self.assertEqual(
            notificaciones[0].prioridad,
            Notificacion.Prioridad.ALTA,
        )

        self.assertFalse(
            notificaciones[0].leida,
        )

        self.assertFalse(
            notificaciones[1].leida,
        )

    def test_crear_notificaciones_con_entidad(self):
        entidad = Usuario.objects.create_user(
            username="entidad_test",
            email="entidad@test.com",
            password="TestPassword123",
        )

        notificaciones = crear_notificaciones(
            usuarios=[
                self.usuario_1,
                self.usuario_2,
            ],
            tipo="prueba.entidad.multiple",
            titulo="Notificación con entidad",
            mensaje="Mensaje asociado a una entidad.",
            entidad=entidad,
        )

        self.assertEqual(
            len(notificaciones),
            2,
        )

        for notificacion in notificaciones:
            self.assertEqual(
                notificacion.entidad_tipo,
                "usuarios.usuario",
            )

            self.assertEqual(
                notificacion.entidad_id,
                entidad.id,
            )

    def test_crear_notificaciones_con_entidad_no_guardada(self):
        entidad = Usuario(
            username="entidad_no_guardada",
            email="entidad_no_guardada@test.com",
        )

        with self.assertRaises(ValueError):
            crear_notificaciones(
                usuarios=[
                    self.usuario_1,
                    self.usuario_2,
                ],
                tipo="prueba.entidad",
                titulo="Notificación",
                mensaje="Mensaje",
                entidad=entidad,
            )


class MarcarComoLeidaTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario_test",
            email="usuario@test.com",
            password="TestPassword123",
        )

        self.otro_usuario = Usuario.objects.create_user(
            username="otro_usuario",
            email="otro@test.com",
            password="TestPassword123",
        )

        self.notificacion = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación de prueba",
            mensaje="Mensaje de prueba",
        )

    def test_marcar_como_leida(self):
        resultado = marcar_como_leida(
            usuario=self.usuario,
            notificacion_id=self.notificacion.id,
        )

        self.assertTrue(resultado.leida)
        self.assertIsNotNone(resultado.fecha_lectura)

        resultado.refresh_from_db()

        self.assertTrue(resultado.leida)
        self.assertIsNotNone(resultado.fecha_lectura)

    def test_no_puede_marcar_notificacion_de_otro_usuario(self):
        with self.assertRaises(Notificacion.DoesNotExist):
            marcar_como_leida(
                usuario=self.otro_usuario,
                notificacion_id=self.notificacion.id,
            )

    def test_notificacion_ya_leida_no_se_modifica(self):
        self.notificacion.leida = True
        self.notificacion.fecha_lectura = timezone.now()
        self.notificacion.save()

        fecha_lectura_original = self.notificacion.fecha_lectura

        resultado = marcar_como_leida(
            usuario=self.usuario,
            notificacion_id=self.notificacion.id,
        )

        self.assertTrue(resultado.leida)
        self.assertEqual(
            resultado.fecha_lectura,
            fecha_lectura_original,
        )


class MarcarTodasComoLeidasTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario_test",
            email="usuario@test.com",
            password="TestPassword123",
        )

        self.otro_usuario = Usuario.objects.create_user(
            username="otro_usuario",
            email="otro@test.com",
            password="TestPassword123",
        )

        self.notificacion_1 = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación 1",
            mensaje="Mensaje 1",
        )

        self.notificacion_2 = Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación 2",
            mensaje="Mensaje 2",
        )

        self.notificacion_otro_usuario = Notificacion.objects.create(
            usuario=self.otro_usuario,
            tipo="prueba",
            titulo="Notificación otro usuario",
            mensaje="Mensaje",
        )

    def test_marcar_todas_como_leidas(self):
        cantidad = marcar_todas_como_leidas(
            usuario=self.usuario,
        )

        self.assertEqual(
            cantidad,
            2,
        )

        self.notificacion_1.refresh_from_db()
        self.notificacion_2.refresh_from_db()

        self.assertTrue(self.notificacion_1.leida)
        self.assertTrue(self.notificacion_2.leida)

        self.assertIsNotNone(
            self.notificacion_1.fecha_lectura
        )

        self.assertIsNotNone(
            self.notificacion_2.fecha_lectura
        )

    def test_no_afecta_notificaciones_de_otro_usuario(self):
        marcar_todas_como_leidas(
            usuario=self.usuario,
        )

        self.notificacion_otro_usuario.refresh_from_db()

        self.assertFalse(
            self.notificacion_otro_usuario.leida
        )

        self.assertIsNone(
            self.notificacion_otro_usuario.fecha_lectura
        )

    def test_no_hay_notificaciones_pendientes(self):
        self.notificacion_1.leida = True
        self.notificacion_1.fecha_lectura = timezone.now()
        self.notificacion_1.save()

        self.notificacion_2.leida = True
        self.notificacion_2.fecha_lectura = timezone.now()
        self.notificacion_2.save()

        cantidad = marcar_todas_como_leidas(
            usuario=self.usuario,
        )

        self.assertEqual(
            cantidad,
            0,
        )


class ContarNoLeidasTests(TestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario_test",
            email="usuario@test.com",
            password="TestPassword123",
        )

        self.otro_usuario = Usuario.objects.create_user(
            username="otro_usuario",
            email="otro@test.com",
            password="TestPassword123",
        )

    def test_contar_no_leidas(self):
        Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación 1",
            mensaje="Mensaje 1",
        )

        Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Notificación 2",
            mensaje="Mensaje 2",
        )

        cantidad = contar_no_leidas(
            usuario=self.usuario,
        )

        self.assertEqual(
            cantidad,
            2,
        )

    def test_no_cuenta_notificaciones_leidas(self):
        Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="No leída",
            mensaje="Mensaje",
        )

        Notificacion.objects.create(
            usuario=self.usuario,
            tipo="prueba",
            titulo="Leída",
            mensaje="Mensaje",
            leida=True,
            fecha_lectura=timezone.now(),
        )

        cantidad = contar_no_leidas(
            usuario=self.usuario,
        )

        self.assertEqual(
            cantidad,
            1,
        )

    def test_no_cuenta_notificaciones_de_otro_usuario(self):
        Notificacion.objects.create(
            usuario=self.otro_usuario,
            tipo="prueba",
            titulo="Notificación otro usuario",
            mensaje="Mensaje",
        )

        cantidad = contar_no_leidas(
            usuario=self.usuario,
        )

        self.assertEqual(
            cantidad,
            0,
        )

    def test_usuario_sin_notificaciones(self):
        cantidad = contar_no_leidas(
            usuario=self.usuario,
        )

        self.assertEqual(
            cantidad,
            0,
        )