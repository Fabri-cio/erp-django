from .models import Auditoria

# Middleware para registrar acciones de los usuarios
class AuditoriaMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        # No registrar logout desde el middleware.
        # Logout se registra directamente en LogoutView.
        if request.path == "/api/auth/logout/":
            return response

        # Solo registrar usuarios autenticados
        if request.user.is_authenticated:

            metodos_auditar = [
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
            ]

            if request.method in metodos_auditar:

                ip = request.META.get(
                    "REMOTE_ADDR"
                )

                Auditoria.objects.create(
                    usuario=request.user,
                    accion=f"{request.method} {request.path}",
                    metodo=request.method,
                    endpoint=request.path,
                    ip=ip,
                    detalle=(
                        f"Respuesta HTTP "
                        f"{response.status_code}"
                    ),
                )

        return response