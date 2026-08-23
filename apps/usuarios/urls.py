from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UsuarioViewSet, GestionarRolesUsuarioView, GestionarPermisosUsuarioView, PermisosEfectivosUsuarioView, CambiarPasswordView, CambiarEstadoUsuarioView


router = DefaultRouter()

router.register("", UsuarioViewSet, basename="usuarios")

urlpatterns = [

    # Cambiar contraseña
    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar-password'),
    
    # Consultar, asignar y eliminar roles de un usuario
    path('<int:user_id>/roles/', GestionarRolesUsuarioView.as_view(), name='gestionar-roles-usuario'),
    
    # Consultar, asignar y eliminar permisos de un usuario
    path('<int:user_id>/permisos/', GestionarPermisosUsuarioView.as_view(), name='gestionar-permisos-usuario'),

    # Consultar permisos efectivos de un usuario
    path('<int:user_id>/permisos-efectivos/', PermisosEfectivosUsuarioView.as_view(), name='permisos-efectivos-usuario'),

    # Cambiar estado de un usuario
    path('<int:user_id>/cambiar-estado/', CambiarEstadoUsuarioView.as_view(), name='cambiar-estado-usuario'),

    # URLs del viewset
    path('', include(router.urls)),
]