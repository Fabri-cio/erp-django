from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.auth.models import Permission

from apps.usuarios.permissions import UsuarioPermission

from .serializers import UsuarioSerializer
from apps.roles.serializers import GestionarPermisosSerializer, GestionarRolesSerializer, PermissionSerializer, RoleSerializer

Usuario = get_user_model()

# Vista para gestionar usuarios
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [UsuarioPermission]

# Vista para gestionar roles de usuarios
class GestionarRolesUsuarioView(APIView):

    # Obtener los roles de un usuario
    @extend_schema(
        responses=RoleSerializer(many=True),
    )
    def get(self, request, user_id):

        try:
            usuario = Usuario.objects.get(id=user_id)

        except Usuario.DoesNotExist:
            return Response(
                {
                    "detail": "Usuario no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        roles = usuario.groups.all()

        serializer = RoleSerializer(
            roles,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # Asignar uno o varios roles
    @extend_schema(
        request=GestionarRolesSerializer,
        responses={200: None},
    )
    def post(self, request, user_id):

        try:
            usuario = Usuario.objects.get(id=user_id)

        except Usuario.DoesNotExist:
            return Response(
                {
                    "detail": "Usuario no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GestionarRolesSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        roles = serializer.validated_data["role_ids"]

        usuario.groups.add(*roles)

        return Response(
            {
                "detail": "Roles asignados correctamente.",
                "user_id": usuario.id,
                "roles": RoleSerializer(
                    roles,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    # Reemplazar todos los roles del usuario
    @extend_schema(
        request=GestionarRolesSerializer,
        responses={200: None},
    )
    def put(self, request, user_id):

        try:
            usuario = Usuario.objects.get(
                id=user_id
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "detail": "Usuario no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GestionarRolesSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        roles = serializer.validated_data["role_ids"]

        # Reemplaza completamente los roles actuales
        usuario.groups.set(roles)

        return Response(
            {
                "detail": "Roles actualizados correctamente.",
                "user_id": usuario.id,
                "roles": RoleSerializer(
                    roles,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    # Eliminar uno o varios roles
    @extend_schema(
        request=GestionarRolesSerializer,
        responses={200: None},
    )
    def delete(self, request, user_id):

        try:
            usuario = Usuario.objects.get(
                id=user_id
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "detail": "Usuario no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GestionarRolesSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        roles = serializer.validated_data["role_ids"]

        roles_no_asignados = [
            role for role in roles
            if not usuario.groups.filter(
                id=role.id
            ).exists()
        ]

        if roles_no_asignados:
            return Response(
                {
                    "detail": (
                        "Uno o más roles no están "
                        "asignados al usuario."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario.groups.remove(*roles)

        return Response(
            {
                "detail": "Roles eliminados correctamente.",
                "user_id": usuario.id,
                "roles": RoleSerializer(
                    roles,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

# Vista para gestionar permisos de un usuario
class GestionarPermisosUsuarioView(APIView):

    # Obtener permisos directos de un usuario
    @extend_schema(
        responses=PermissionSerializer(many=True),
    )
    def get(self, request, user_id):

        try:
            usuario = Usuario.objects.get(
                id=user_id
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "detail": "Usuario no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        permisos = usuario.user_permissions.all()

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
    def post(self, request, user_id):

        try:
            usuario = Usuario.objects.get(
                id=user_id
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "detail": "Usuario no encontrado."
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

        usuario.user_permissions.add(
            *permisos
        )

        return Response(
            {
                "detail": (
                    "Permisos asignados correctamente."
                ),
                "user_id": usuario.id,
                "permissions": PermissionSerializer(
                    permisos,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

    # Reemplazar todos los permisos directos
    @extend_schema(
        request=GestionarPermisosSerializer,
        responses={200: None},
    )
    def put(self, request, user_id):

        try:
            usuario = Usuario.objects.get(
                id=user_id
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "detail": "Usuario no encontrado."
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

        usuario.user_permissions.set(
            permisos
        )

        return Response(
            {
                "detail": (
                    "Permisos actualizados correctamente."
                ),
                "user_id": usuario.id,
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
    def delete(self, request, user_id):

        try:
            usuario = Usuario.objects.get(
                id=user_id
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "detail": "Usuario no encontrado."
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
            if not usuario.user_permissions.filter(
                id=permission.id
            ).exists()
        ]

        if permisos_no_asignados:

            return Response(
                {
                    "detail": (
                        "Uno o más permisos no están "
                        "asignados directamente al usuario."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario.user_permissions.remove(
            *permisos
        )

        return Response(
            {
                "detail": (
                    "Permisos eliminados correctamente."
                ),
                "user_id": usuario.id,
                "permissions": PermissionSerializer(
                    permisos,
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )

# Vista para consultar permisos efectivos de un usuario
class PermisosEfectivosUsuarioView(APIView):

    @extend_schema(
        responses=PermissionSerializer(many=True),
    )
    def get(self, request, user_id):

        try:
            usuario = Usuario.objects.get(
                id=user_id
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "detail": "Usuario no encontrado."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Permisos directos del usuario
        permisos_directos = usuario.user_permissions.all()

        # Permisos heredados de los roles
        permisos_roles = Permission.objects.filter(
            group__user=usuario
        )

        # Unir permisos directos + permisos de roles
        permisos_efectivos = Permission.objects.filter(
            Q(
                id__in=permisos_directos.values_list(
                    "id",
                    flat=True,
                )
            )
            |
            Q(
                id__in=permisos_roles.values_list(
                    "id",
                    flat=True,
                )
            )
        ).distinct()

        serializer = PermissionSerializer(
            permisos_efectivos,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
