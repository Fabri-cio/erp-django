from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers


Usuario = get_user_model()


# Serializer para solicitar restablecimiento de contraseña
class PasswordResetRequestSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=True
    )

    def validate(self, attrs):

        email = attrs["email"]

        try:
            usuario = Usuario.objects.get(
                email__iexact=email
            )
        except Usuario.DoesNotExist:

            # No revelar si el correo existe
            attrs["usuario"] = None
            return attrs

        # Si el usuario existe pero está desactivado,
        # tampoco revelamos esa información.
        if not usuario.is_active:
            attrs["usuario"] = None
            return attrs

        attrs["usuario"] = usuario

        return attrs


# Serializer para confirmar restablecimiento de contraseña
class PasswordResetConfirmSerializer(serializers.Serializer):

    uid = serializers.CharField(
        required=True
    )

    token = serializers.CharField(
        required=True
    )

    password_nueva = serializers.CharField(
        write_only=True,
        required=True
    )

    password_nueva_confirmacion = serializers.CharField(
        write_only=True,
        required=True
    )

    def validate(self, attrs):

        try:

            user_id = urlsafe_base64_decode(
                attrs["uid"]
            ).decode()

            usuario = Usuario.objects.get(
                pk=user_id
            )

        except (
            ValueError,
            TypeError,
            OverflowError,
            Usuario.DoesNotExist,
        ):

            raise serializers.ValidationError(
                {
                    "uid": (
                        "El usuario de recuperación "
                        "no es válido."
                    )
                }
            )

        # Verificar token
        if not default_token_generator.check_token(
            usuario,
            attrs["token"]
        ):

            raise serializers.ValidationError(
                {
                    "token": (
                        "El token no es válido "
                        "o ha expirado."
                    )
                }
            )

        # Confirmar contraseña
        if (
            attrs["password_nueva"]
            != attrs["password_nueva_confirmacion"]
        ):

            raise serializers.ValidationError(
                {
                    "password_nueva_confirmacion": (
                        "Las contraseñas nuevas "
                        "no coinciden."
                    )
                }
            )

        # Validadores configurados en Django
        validate_password(
            attrs["password_nueva"],
            usuario,
        )

        attrs["usuario"] = usuario

        return attrs