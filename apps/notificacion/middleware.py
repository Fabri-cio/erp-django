from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


Usuario = get_user_model()


@database_sync_to_async
def obtener_usuario(token):
    """
    Valida un token JWT y obtiene el usuario correspondiente.

    Esta función se ejecuta de forma segura fuera del contexto
    principal del consumidor WebSocket, ya que la consulta al ORM
    de Django es una operación síncrona.

    El usuario debe:
        - Tener un token JWT válido.
        - Contener un `user_id` válido.
        - Existir en la base de datos.
        - Estar activo.

    Args:
        token:
            Token JWT de acceso recibido durante la conexión
            WebSocket.

    Returns:
        Usuario | None:
            Instancia del usuario autenticado si el token es válido
            y el usuario existe y está activo. En caso contrario,
            retorna `None`.
    """

    try:
        access_token = AccessToken(token)

        user_id = access_token["user_id"]

        return Usuario.objects.get(
            id=user_id,
            is_active=True,
        )

    except (
        InvalidToken,
        TokenError,
        Usuario.DoesNotExist,
    ):
        return None


class JWTAuthMiddleware:
    """
    Middleware de autenticación JWT para conexiones WebSocket.

    Django REST Framework autentica automáticamente las peticiones
    HTTP mediante JWT, pero esa autenticación no se aplica
    automáticamente a las conexiones WebSocket.

    Este middleware adapta el JWT de SimpleJWT al sistema de
    autenticación de Django Channels.

    Flujo:

        WebSocket
            ↓
        ?token=<JWT>
            ↓
        JWTAuthMiddleware
            ↓
        validar token
            ↓
        obtener usuario
            ↓
        scope["user"]
            ↓
        NotificacionConsumer

    El middleware no contiene lógica de negocio ni depende de
    ningún módulo funcional del ERP.

    Su única responsabilidad es identificar al usuario que realiza
    la conexión WebSocket.
    """

    def __init__(self, app):
        """
        Inicializa el middleware.

        Args:
            app:
                Aplicación ASGI que recibirá la conexión después
                de procesarse la autenticación.
        """

        self.app = app

    async def __call__(
        self,
        scope,
        receive,
        send,
    ):
        """
        Procesa una conexión WebSocket y establece el usuario
        autenticado dentro de `scope["user"]`.

        El token se obtiene actualmente desde el parámetro
        `token` de la cadena de consulta:

            ?token=<JWT>

        Si no existe un token válido, se establece `user` como
        `None`. El consumer será responsable de rechazar la
        conexión no autenticada.

        Args:
            scope:
                Información de la conexión ASGI.

            receive:
                Canal ASGI utilizado para recibir eventos.

            send:
                Canal ASGI utilizado para enviar eventos.
        """

        query_string = scope.get(
            "query_string",
            b"",
        ).decode()

        query_params = parse_qs(
            query_string
        )

        token = query_params.get(
            "token",
            [None],
        )[0]

        if not token:
            scope["user"] = None
        else:
            scope["user"] = await obtener_usuario(
                token
            )

        return await self.app(
            scope,
            receive,
            send,
        )
