from rest_framework import viewsets
from rest_framework.views import APIView, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Usuario
from .serializers import UsuarioSerializer
from apps.roles.serializers import AssignRoleSerializer
from .permissions import UsuarioPermission
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [UsuarioPermission]

@extend_schema(
    request=AssignRoleSerializer,
    responses={200: None}
)
class AssignRoleViewSet(APIView):
    # Asignar un rol a un usuario
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

        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role = serializer.validated_data["role"]

        usuario.groups.add(role)

        return Response(
            {
                "detail": "Rol asignado correctamente.",
                "user_id": usuario.id,
                "role_id": role.id,
                "role": role.name,
            },
            status=status.HTTP_200_OK,
        )