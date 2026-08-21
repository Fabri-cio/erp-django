from django.urls import path

from .views import PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    # Restablecimiento de contraseña
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),

    # Confirmación de restablecimiento
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
