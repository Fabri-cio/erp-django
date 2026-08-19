from rest_framework.permissions import BasePermission


class RolPermission(BasePermission):

    # Mapeo de permisos por método HTTP
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    # Verificar permisos basados en el método HTTP
    def has_permission(self, request, view):
        # Si es superusuario, permitir acceso
        if request.user.is_superuser:
            return True

        model = view.queryset.model

        required_permissions = self.perms_map.get(request.method, [])

        # Verificar si el usuario tiene los permisos requeridos
        return request.user.has_perms(
            [
                permission % {
                    "app_label": model._meta.app_label,
                    "model_name": model._meta.model_name,
                }
                for permission in required_permissions
            ]
        )

# Permisos para gestionar permisos de un rol
class GestionarPermisosRolPermission(BasePermission):

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.change_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.change_%(model_name)s"],
    }

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        required_permissions = self.perms_map.get(
            request.method,
            []
        )

        return request.user.has_perms(
            [
                permission % {
                    "app_label": "auth",
                    "model_name": "group",
                }
                for permission in required_permissions
            ]
        )