from asgiref.sync import async_to_sync

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.notificacion.middleware import JWTAuthMiddleware


Usuario = get_user_model()


class JWTAuthMiddlewareTests(TransactionTestCase):

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username="usuario1",
            email="usuario1@test.com",
            password="testpass123",
            is_active=True,
        )

        self.usuario_recibido = None

    # =========================================================
    # ASGI RECEIVE / SEND
    # =========================================================

    async def receive(self):
        return {
            "type": "websocket.disconnect",
        }

    async def send(self, message):
        pass

    # =========================================================
    # APLICACIÓN ASGI DE PRUEBA
    # =========================================================

    async def app(self, scope, receive, send):
        """
        Aplicación ASGI de prueba.

        Guarda el usuario recibido en scope para verificar
        que el middleware haya identificado correctamente
        al usuario.
        """
        self.usuario_recibido = scope.get("user")

    # =========================================================
    # HELPER
    # =========================================================

    def ejecutar_middleware(self, token=None):
        middleware = JWTAuthMiddleware(self.app)

        query_string = ""

        if token is not None:
            query_string = f"token={token}"

        scope = {
            "type": "websocket",
            "query_string": query_string.encode(),
        }

        async_to_sync(middleware)(
            scope,
            self.receive,
            self.send,
        )

        return scope

    # =========================================================
    # TOKEN VÁLIDO
    # =========================================================

    def test_token_valido_identifica_usuario(self):
        token = str(
            AccessToken.for_user(self.usuario)
        )

        scope = self.ejecutar_middleware(token)

        self.assertEqual(
            scope["user"],
            self.usuario,
        )

        self.assertEqual(
            scope["user"].id,
            self.usuario.id,
        )

    # =========================================================
    # SIN TOKEN
    # =========================================================

    def test_sin_token_no_identifica_usuario(self):
        scope = self.ejecutar_middleware()

        self.assertIsNone(
            scope["user"],
        )

    # =========================================================
    # TOKEN VACÍO
    # =========================================================

    def test_token_vacio_no_identifica_usuario(self):
        scope = self.ejecutar_middleware("")

        self.assertIsNone(
            scope["user"],
        )

    # =========================================================
    # TOKEN INVÁLIDO
    # =========================================================

    def test_token_invalido_no_identifica_usuario(self):
        scope = self.ejecutar_middleware(
            "token-invalido",
        )

        self.assertIsNone(
            scope["user"],
        )

    # =========================================================
    # USUARIO INACTIVO
    # =========================================================

    def test_usuario_inactivo_no_identifica_usuario(self):
        self.usuario.is_active = False

        self.usuario.save(
            update_fields=["is_active"],
        )

        token = str(
            AccessToken.for_user(self.usuario)
        )

        scope = self.ejecutar_middleware(token)

        self.assertIsNone(
            scope["user"],
        )

    # =========================================================
    # USUARIO INEXISTENTE
    # =========================================================

    def test_usuario_inexistente_no_identifica_usuario(self):
        token = str(
            AccessToken.for_user(self.usuario)
        )

        self.usuario.delete()

        scope = self.ejecutar_middleware(token)

        self.assertIsNone(
            scope["user"],
        )

    # =========================================================
    # REFRESH TOKEN
    # =========================================================

    def test_refresh_token_no_identifica_usuario(self):
        refresh = RefreshToken.for_user(
            self.usuario,
        )

        scope = self.ejecutar_middleware(
            str(refresh),
        )

        self.assertIsNone(
            scope["user"],
        )

    # =========================================================
    # TOKEN EN QUERY STRING
    # =========================================================

    def test_token_se_lee_desde_query_string(self):
        token = str(
            AccessToken.for_user(self.usuario)
        )

        scope = {
            "type": "websocket",
            "query_string": (
                f"token={token}"
            ).encode(),
        }

        middleware = JWTAuthMiddleware(self.app)

        async_to_sync(middleware)(
            scope,
            None,
            None,
        )

        self.assertEqual(
            scope["user"].id,
            self.usuario.id,
        )

    # =========================================================
    # EL MIDDLEWARE ENTREGA EL SCOPE
    # =========================================================

    def test_middleware_entrega_scope_a_la_aplicacion(self):
        token = str(
            AccessToken.for_user(self.usuario)
        )

        self.ejecutar_middleware(token)

        self.assertEqual(
            self.usuario_recibido.id,
            self.usuario.id,
        )