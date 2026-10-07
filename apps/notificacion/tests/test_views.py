from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from apps.notificacion.models import Notificacion

Usuario = get_user_model()


class NotificacionViewSetTests(APITestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario1",
            email="usuario1@test.com",
            password="testpass123",
        )

        self.otro_usuario = Usuario.objects.create_user(
            username="usuario2",
            email="usuario2@test.com",
            password="testpass123",
        )

        self.client.force_authenticate(user=self.usuario)

    def crear_notificacion(
        self,
        usuario,
        *,
        titulo="Notificación de prueba",
        leida=False,
    ):
        return Notificacion.objects.create(
            usuario=usuario,
            tipo="PRUEBA",
            titulo=titulo,
            mensaje="Mensaje de prueba",
            prioridad=Notificacion.Prioridad.MEDIA,
            leida=leida,
        )

    # =========================================================
    # LISTAR
    # =========================================================

    def test_listar_notificaciones_solo_del_usuario_autenticado(self):
        propia1 = self.crear_notificacion(
            self.usuario,
            titulo="Notificación propia 1",
        )

        propia2 = self.crear_notificacion(
            self.usuario,
            titulo="Notificación propia 2",
        )

        otra = self.crear_notificacion(
            self.otro_usuario,
            titulo="Notificación de otro usuario",
        )

        response = self.client.get("/api/notificaciones/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        resultados = response.data

        ids = [item["id"] for item in resultados]

        self.assertIn(propia1.id, ids)
        self.assertIn(propia2.id, ids)
        self.assertNotIn(otra.id, ids)

        self.assertEqual(
            len(resultados),
            2,
        )

    # =========================================================
    # DETALLE
    # =========================================================

    def test_consultar_notificacion_propia(self):
        notificacion = self.crear_notificacion(
            self.usuario,
        )

        response = self.client.get(
            f"/api/notificaciones/{notificacion.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            notificacion.id,
        )

    def test_no_puede_consultar_notificacion_de_otro_usuario(self):
        notificacion = self.crear_notificacion(
            self.otro_usuario,
        )

        response = self.client.get(
            f"/api/notificaciones/{notificacion.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # =========================================================
    # MARCAR UNA COMO LEÍDA
    # =========================================================

    def test_marcar_notificacion_como_leida(self):
        notificacion = self.crear_notificacion(
            self.usuario,
            leida=False,
        )

        response = self.client.post(
            f"/api/notificaciones/{notificacion.id}/marcar-leida/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        notificacion.refresh_from_db()

        self.assertTrue(
            notificacion.leida,
        )

        self.assertIsNotNone(
            notificacion.fecha_lectura,
        )

        self.assertTrue(
            response.data["leida"],
        )

    def test_no_puede_marcar_notificacion_de_otro_usuario(self):
        notificacion = self.crear_notificacion(
            self.otro_usuario,
            leida=False,
        )

        response = self.client.post(
            f"/api/notificaciones/{notificacion.id}/marcar-leida/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        notificacion.refresh_from_db()

        self.assertFalse(
            notificacion.leida,
        )

    # =========================================================
    # MARCAR TODAS COMO LEÍDAS
    # =========================================================

    def test_marcar_todas_como_leidas(self):
        notificacion1 = self.crear_notificacion(
            self.usuario,
            titulo="Pendiente 1",
            leida=False,
        )

        notificacion2 = self.crear_notificacion(
            self.usuario,
            titulo="Pendiente 2",
            leida=False,
        )

        notificacion_leida = self.crear_notificacion(
            self.usuario,
            titulo="Ya leída",
            leida=True,
        )

        response = self.client.post(
            "/api/notificaciones/marcar-todas-leidas/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["actualizadas"],
            2,
        )

        notificacion1.refresh_from_db()
        notificacion2.refresh_from_db()
        notificacion_leida.refresh_from_db()

        self.assertTrue(
            notificacion1.leida,
        )

        self.assertTrue(
            notificacion2.leida,
        )

        self.assertTrue(
            notificacion_leida.leida,
        )

        self.assertIsNotNone(
            notificacion1.fecha_lectura,
        )

        self.assertIsNotNone(
            notificacion2.fecha_lectura,
        )

    def test_marcar_todas_no_afecta_a_otro_usuario(self):
        propia = self.crear_notificacion(
            self.usuario,
            leida=False,
        )

        ajena = self.crear_notificacion(
            self.otro_usuario,
            leida=False,
        )

        response = self.client.post(
            "/api/notificaciones/marcar-todas-leidas/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        propia.refresh_from_db()
        ajena.refresh_from_db()

        self.assertTrue(
            propia.leida,
        )

        self.assertFalse(
            ajena.leida,
        )

    def test_marcar_todas_sin_pendientes(self):
        self.crear_notificacion(
            self.usuario,
            leida=True,
        )

        response = self.client.post(
            "/api/notificaciones/marcar-todas-leidas/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["actualizadas"],
            0,
        )

    # =========================================================
    # CONTADOR
    # =========================================================

    def test_contador_no_leidas(self):
        self.crear_notificacion(
            self.usuario,
            leida=False,
        )

        self.crear_notificacion(
            self.usuario,
            leida=False,
        )

        self.crear_notificacion(
            self.usuario,
            leida=True,
        )

        response = self.client.get(
            "/api/notificaciones/contador-no-leidas/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["no_leidas"],
            2,
        )

    def test_contador_no_cuenta_notificaciones_de_otro_usuario(self):
        self.crear_notificacion(
            self.usuario,
            leida=False,
        )

        self.crear_notificacion(
            self.otro_usuario,
            leida=False,
        )

        response = self.client.get(
            "/api/notificaciones/contador-no-leidas/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["no_leidas"],
            1,
        )

    # =========================================================
    # AUTENTICACIÓN
    # =========================================================

    def test_usuario_no_autenticado_no_puede_listar(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            "/api/notificaciones/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_usuario_no_autenticado_no_puede_consultar_contador(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            "/api/notificaciones/contador-no-leidas/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # =========================================================
    # SOLO LECTURA
    # =========================================================

    def test_no_puede_crear_notificacion_desde_api(self):
        response = self.client.post(
            "/api/notificaciones/",
            {
                "tipo": "PRUEBA",
                "titulo": "Intento de creación",
                "mensaje": "No debería crearse",
                "prioridad": "media",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertEqual(
            Notificacion.objects.count(),
            0,
        )

    def test_no_puede_eliminar_notificacion_desde_api(self):
        notificacion = self.crear_notificacion(
            self.usuario,
        )

        response = self.client.delete(
            f"/api/notificaciones/{notificacion.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED,
        )

        self.assertTrue(
            Notificacion.objects.filter(
                id=notificacion.id,
            ).exists()
        )