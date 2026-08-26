from django.conf import settings
from django.db import models

# Modelo para registrar acciones de los usuarios
class Auditoria(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="auditorias",
    )

    accion = models.CharField(
        max_length=100
    )

    metodo = models.CharField(
        max_length=10
    )

    endpoint = models.CharField(
        max_length=255
    )

    ip = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    detalle = models.TextField(
        blank=True,
        default="",
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.accion} - {self.usuario}"