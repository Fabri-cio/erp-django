from rest_framework import serializers
from django.contrib.auth.models import Group


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
