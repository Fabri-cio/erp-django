from rest_framework import viewsets
from django.contrib.auth.models import Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .serializers import RoleSerializer, PermissionSerializer, GestionarPermisosSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    # permission_classes = [RolPermission] # Permisos personalizados

# Vista para gestionar permisos de un rol
class GestionarPermisosRolView(APIView):

    # Obtener permisos del rol
    @extend_schema(
        responses=PermissionSerializer(many=True),
    )
    def get(self, request, role_id):

        try:
            rol = Group.objects.get(
                id=role_id
            )

        except Group.DoesNotExist:

            return Response(
                {
                    "detail": "Rol no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        permisos = rol.permissions.all()

        serializer = PermissionSerializer(
            permisos,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # Agregar uno o varios permisos
    @extend_schema(
        request=GestionarPermisosSerializer,
        responses={200: None},
    )
    def post(self, request, role_id):

        try:
            rol = Group.objects.get(
                id=role_id
            )

        except Group.DoesNotExist:

            return Response(
                {
                    "detail": "Rol no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GestionarPermisosSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        permisos = serializer.validated_data[
            "permission_ids"
        ]

        rol.permissions.add(
            *permisos
        )

        return Response(
            {
                "detail": (
                    "Permisos asignados correctamente al rol."
                ),
                "role_id": rol.id,
                "permissions": PermissionSerializer(
                    permisos,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    # Reemplazar todos los permisos del rol
    @extend_schema(
        request=GestionarPermisosSerializer,
        responses={200: None},
    )
    def put(self, request, role_id):

        try:
            rol = Group.objects.get(
                id=role_id
            )

        except Group.DoesNotExist:

            return Response(
                {
                    "detail": "Rol no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GestionarPermisosSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        permisos = serializer.validated_data[
            "permission_ids"
        ]

        rol.permissions.set(
            permisos
        )

        return Response(
            {
                "detail": (
                    "Permisos del rol actualizados correctamente."
                ),
                "role_id": rol.id,
                "permissions": PermissionSerializer(
                    permisos,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    # Eliminar uno o varios permisos
    @extend_schema(
        request=GestionarPermisosSerializer,
        responses={200: None},
    )
    def delete(self, request, role_id):

        try:
            rol = Group.objects.get(
                id=role_id
            )

        except Group.DoesNotExist:

            return Response(
                {
                    "detail": "Rol no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GestionarPermisosSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        permisos = serializer.validated_data[
            "permission_ids"
        ]

        permisos_no_asignados = [
            permission
            for permission in permisos
            if not rol.permissions.filter(
                id=permission.id
            ).exists()
        ]

        if permisos_no_asignados:

            return Response(
                {
                    "detail": (
                        "Uno o más permisos no están "
                        "asignados al rol."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        rol.permissions.remove(
            *permisos
        )

        return Response(
            {
                "detail": (
                    "Permisos eliminados correctamente."
                ),
                "role_id": rol.id,
                "permissions": PermissionSerializer(
                    permisos,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )