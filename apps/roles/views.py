from rest_framework import viewsets
from django.contrib.auth.models import Group
from .serializers import RoleSerializer
from .permissions import RolPermission

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [RolPermission] # Permisos personalizados