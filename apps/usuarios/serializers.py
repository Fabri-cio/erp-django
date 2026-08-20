from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    # Campo password solo para escritura
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'is_active',
            'last_login',
            'date_joined',
        ]

        # Campos solo lectura
        read_only_fields = [
            'id',
            'last_login',
            'date_joined',
        ]

    # Validar contraseña 
    def validate_password(self, value):
        validate_password(value)
        return value

    # Crear usuario
    def create(self, validated_data):
        password = validated_data.pop('password')

        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        
        return usuario

    # Actualizar usuario
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

# Serializer para cambiar contraseña
class CambiarPasswordSerializer(serializers.Serializer):
    
    password_actual = serializers.CharField(
        write_only=True,
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

    # Validar contraseña
    def validate(self, attrs):
        
        usuario = self.context['request'].user
        
        # Verificar contraseña actual
        if not usuario.check_password(
            attrs["password_actual"]
        ):
            raise serializers.ValidationError(
                {
                    "password_actual": (
                        "La contraseña actual es incorrecta."
                    )
                }
            )

        # Confirmar nueva contraseña
        if (
            attrs["password_nueva"]
            != attrs["password_nueva_confirmacion"]
        ):
            raise serializers.ValidationError(
                {
                    "password_nueva_confirmacion": (
                        "Las contraseñas nuevas no coinciden."
                    )
                }
            )

        # Ejecutar validadores de contraseña de Django
        validate_password(
            attrs["password_nueva"],
            usuario,
        )

        return attrs