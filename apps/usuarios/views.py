from rest_framework import viewsets

from .models import Usuario
from .serializers import UsuarioSerializer
from .permissions import UsuarioPermission


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [UsuarioPermission]