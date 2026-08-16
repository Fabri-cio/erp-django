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
