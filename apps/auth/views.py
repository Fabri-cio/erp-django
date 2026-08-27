from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.auditoria.models import Auditoria

from .serializers import (LoginSerializer, LogoutSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer)


# Vista para solicitar restablecimiento de contraseña
class PasswordResetRequestView(APIView):

    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=PasswordResetRequestSerializer,
        responses={
            200: None,
        },
    )
    def post(self, request):

        serializer = PasswordResetRequestSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        usuario = serializer.validated_data.get(
            "usuario"
        )

        # No hacer nada si el correo no existe
        # o el usuario está desactivado.
        if usuario is not None:

            token = default_token_generator.make_token(
                usuario
            )

            uid = urlsafe_base64_encode(
                force_bytes(usuario.pk)
            )

            # Enlace que posteriormente utilizará
            # el frontend para restablecer la contraseña.
            reset_url = (
                "http://localhost:3000/"
                f"reset-password/{uid}/{token}/"
            )

            send_mail(
                subject="Restablecimiento de contraseña",
                message=(
                    "Has solicitado restablecer "
                    "tu contraseña.\n\n"
                    "Ingresa al siguiente enlace:\n\n"
                    f"{reset_url}\n\n"
                    "Si no realizaste esta solicitud, "
                    "puedes ignorar este correo."
                ),
                from_email=None,
                recipient_list=[
                    usuario.email
                ],
                fail_silently=False,
            )

        # Respuesta genérica para no revelar
        # si el correo existe.
        return Response(
            {
                "detail": (
                    "Si el correo está registrado, "
                    "recibirás instrucciones para "
                    "restablecer tu contraseña."
                )
            },
            status=status.HTTP_200_OK,
        )


# Vista para confirmar restablecimiento de contraseña
class PasswordResetConfirmView(APIView):

    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=PasswordResetConfirmSerializer,
        responses={
            200: None,
        },
    )
    def post(self, request):

        serializer = PasswordResetConfirmSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        usuario = serializer.validated_data[
            "usuario"
        ]

        usuario.set_password(
            serializer.validated_data[
                "password_nueva"
            ]
        )

        usuario.save(
            update_fields=[
                "password"
            ]
        )

        return Response(
            {
                "detail": (
                    "Contraseña restablecida "
                    "correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

# Vista para cerrar sesión
class LogoutView(APIView):

    authentication_classes = []
    permission_classes = []

    @extend_schema(
        request=LogoutSerializer,
        responses={
            200: None,
        },
    )
    def post(self, request):

        serializer = LogoutSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        refresh_token = serializer.validated_data[
            "refresh"
        ]

        try:

            token = RefreshToken(
                refresh_token
            )

            # Obtener el ID del usuario para registrar la auditoría
            usuario_id = token.get(
                "user_id"
            )

            token.blacklist()

        except Exception:
            return Response(
                {
                    "detail": (
                        "El refresh token no es válido "
                        "o ya fue revocado."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Registrar la auditoría
        Auditoria.objects.create(
            usuario_id=usuario_id,
            accion="Cierre de sesion",
            metodo="POST",
            endpoint="/api/auth/logout/",
            ip=request.META.get("REMOTE_ADDR"),
            detalle="Logout exitoso",
        )

        return Response(
            {
                "detail": (
                    "Sesión cerrada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )

# Consultar sesiones activas
class SesionesUsuarioView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        responses={
            200: None,
        },
    )
    def get(self, request):

        tokens = OutstandingToken.objects.filter(
            user=request.user
        ).order_by(
            "-created_at"
        )

        # Solucion al n+1 query
        # Obtener los tokens revocados
        tokens_revocados = set(
            BlacklistedToken.objects.filter(
                token__in=tokens
            ).values_list(
                "token_id",
                flat=True,
            )
        )

        # Construir la lista de sesiones
        sesiones = [
            {
                "id": token.id,
                "created_at": token.created_at,
                "expires_at": token.expires_at,
                "revocado": token.id in tokens_revocados,
            }
            for token in tokens
        ]

        return Response(
            sesiones,
            status=status.HTTP_200_OK,
        )


# Cerrar una sesión específica
class CerrarSesionView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        responses={
            200: None,
        },
    )
    def delete(self, request, token_id):

        try:
            token = OutstandingToken.objects.get(
                id=token_id,
                user=request.user,
            )

        except OutstandingToken.DoesNotExist:

            return Response(
                {
                    "detail": (
                        "La sesión no existe."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        BlacklistedToken.objects.get_or_create(
            token=token
        )

        return Response(
            {
                "detail": (
                    "Sesión cerrada correctamente."
                )
            },
            status=status.HTTP_200_OK,
        )


# Cerrar todas las sesiones del usuario
class CerrarTodasSesionesView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    @extend_schema(
        responses={
            200: None,
        },
    )
    def post(self, request):

        tokens = OutstandingToken.objects.filter(
            user=request.user
        )

        contador = 0

        for token in tokens:

            _, creado = BlacklistedToken.objects.get_or_create(
                token=token
            )

            if creado:
                contador += 1

        return Response(
            {
                "detail": (
                    "Todas las sesiones "
                    "fueron cerradas correctamente."
                ),
                "sesiones_cerradas": contador,
            },
            status=status.HTTP_200_OK,
        )

# Vista personalizada para login con auditoría
class LoginView(TokenObtainPairView):

    serializer_class = LoginSerializer

