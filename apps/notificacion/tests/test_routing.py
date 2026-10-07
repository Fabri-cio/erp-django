from django.test import SimpleTestCase

from apps.notificacion.routing import websocket_urlpatterns


class NotificacionRoutingTests(SimpleTestCase):

    def test_existe_ruta_de_notificaciones(self):
        self.assertEqual(
            len(websocket_urlpatterns),
            1,
        )

    def test_ruta_de_notificaciones_es_correcta(self):
        pattern = websocket_urlpatterns[0]

        self.assertEqual(
            pattern.pattern.regex.pattern,
            r"ws/notificaciones/$",
        )

    def test_ruta_es_websocket(self):
        pattern = websocket_urlpatterns[0]

        self.assertTrue(
            pattern.pattern.match(
                "ws/notificaciones/"
            )
        )

        self.assertIsNone(
            pattern.pattern.match(
                "api/notificaciones/"
            )
        )