from rest_framework.permissions import DjangoModelPermissions, BasePermission

# Permisos para la app usuarios
class UsuarioPermission(DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

# Permisos para gestionar permisos de usuarios
class GestionarPermisosUsuarioPermission(BasePermission):

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.change_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.change_%(model_name)s"],
    }

    def has_permission(self, request, view):

        # Usuario no autenticado
        if not request.user.is_authenticated:
            return False

        # Superusuario
        if request.user.is_superuser:
            return True

        required_permissions = self.perms_map.get(
            request.method,
            []
        )

        return request.user.has_perms(
            [
                permission % {
                    "app_label": "usuarios",
                    "model_name": "usuario",
                }
                for permission in required_permissions
            ]
        )

# Permisos para consultar permisos efectivos de usuarios
class PermisosEfectivosUsuarioPermission(BasePermission):

    def has_permission(self, request, view):

        # Usuario no autenticado
        if not request.user.is_authenticated:
            return False

        # Superusuario
        if request.user.is_superuser:
            return True

        # Solo permitir GET
        if request.method != "GET":
            return False

        # Permiso necesario para consultar el usuario
        return request.user.has_perm(
            "usuarios.view_usuario"
        )

# Permisos para gestionar roles de usuarios
class GestionarRolesUsuarioPermission(BasePermission):

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.change_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.change_%(model_name)s"],
    }

    def has_permission(self, request, view):

        # Usuario no autenticado
        if not request.user.is_authenticated:
            return False

        # Superusuario
        if request.user.is_superuser:
            return True

        required_permissions = self.perms_map.get(
            request.method,
            []
        )

        return request.user.has_perms(
            [
                permission % {
                    "app_label": "usuarios",
                    "model_name": "usuario",
                }
                for permission in required_permissions
            ]
        )

# Permisos para cambiar estado de usuario
class CambiarEstadoUsuarioPermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return request.user.has_perm(
            "usuarios.change_usuario"
        )