from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from .serializers import (PasswordResetRequestSerializer, PasswordResetConfirmSerializer)


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