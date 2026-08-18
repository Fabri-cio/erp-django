from rest_framework import serializers
from django.contrib.auth.models import Group, Permission

# Serializer para mostrar roles
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
        ]

        # Campos solo lectura
        read_only_fields = [
            'id',
        ]

# Serializer para gestionar roles (obtener, asignar y eliminar por id de usuario)
class GestionarRolesSerializer(serializers.Serializer):

    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
    )

# Serializer para mostrar permisos
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            'id',
            'name',
            'codename',
            'content_type',
        ]

        # Campos solo lectura
        read_only_fields = [
            'id',
        ]

# Serializer para gestionar permisos (obtener, asignar y eliminar por id de usuario)
class GestionarPermisosSerializer(serializers.Serializer):

    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
    )