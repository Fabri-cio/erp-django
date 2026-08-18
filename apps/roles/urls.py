from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, GestionarPermisosRolView

router = DefaultRouter()
router.register('', RoleViewSet, basename='roles')

urlpatterns = [
    path('', include(router.urls)),

    # Consultar, asignar, actualizar y eliminar permisos de un rol
    path('<int:role_id>/permisos/', GestionarPermisosRolView.as_view(), name='gestionar_permisos_rol'),
]