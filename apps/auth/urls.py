from django.urls import path

from .views import (
LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    SesionesUsuarioView,
    CerrarSesionView,
    CerrarTodasSesionesView,
)

urlpatterns = [
    # Restablecimiento de contraseña
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),

    # Confirmación de restablecimiento
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # Cerrar sesión
    path('logout/', LogoutView.as_view(), name='logout'),

    # Gestión de sesiones
    path('sesiones/', SesionesUsuarioView.as_view(), name='sesiones'),

    path('sesiones/<int:token_id>/', CerrarSesionView.as_view(), name='cerrar-sesion'),

    path('sesiones/cerrar-todas/', CerrarTodasSesionesView.as_view(), name='cerrar-todas-sesiones'),
]
