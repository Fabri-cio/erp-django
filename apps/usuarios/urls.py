from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UsuarioViewSet, GestionarRolesUsuarioView, GestionarPermisosUsuarioView


router = DefaultRouter()

router.register("", UsuarioViewSet, basename="usuarios")

urlpatterns = [
    path('', include(router.urls)),
    
    # Consultar, asignar y eliminar roles de un usuario
    path('<int:user_id>/roles/', GestionarRolesUsuarioView.as_view(), name='gestionar-roles-usuario'),
    
    # Consultar, asignar y eliminar permisos de un usuario
    path('<int:user_id>/permisos/', GestionarPermisosUsuarioView.as_view(), name='gestionar-permisos-usuario'),

]