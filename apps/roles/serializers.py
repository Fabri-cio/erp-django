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

# Serializer para asignar un rol a un usuario
class AssignRoleSerializer(serializers.Serializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        source="role",
    )
