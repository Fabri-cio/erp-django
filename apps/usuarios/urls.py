from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UsuarioViewSet, AssignRoleViewSet


router = DefaultRouter()

router.register("", UsuarioViewSet, basename="usuarios")

urlpatterns = [
    path('', include(router.urls)),
    # Asignar rol a usuario
    path('<int:user_id>/roles/', AssignRoleViewSet.as_view(), name='assign-user-role'),
]