"""
Modelos del módulo de notificaciones.

Este módulo contiene las entidades relacionadas con las
notificaciones internas del sistema.
"""


from django.db import models
from django.conf import settings
# Create your models here.
class Notificacion(models.Model):
    """
    Representa una notificación dirigida a un usuario.

    Una notificación almacena el contenido que debe visualizar
    el usuario, su prioridad, su estado de lectura y, opcionalmente,
    una referencia a la entidad del sistema que originó la
    notificación.

    La notificación pertenece a un usuario específico y no se
    elimina automáticamente cuando el usuario es eliminado,
    debido a la política `PROTECT`.

    La persistencia de las notificaciones se realiza mediante
    este modelo. La creación de notificaciones desde la lógica
    de aplicación debe realizarse mediante los servicios del
    módulo `notificacion`.

    El modelo no es responsable de enviar notificaciones en tiempo
    real. Esa responsabilidad pertenece al publisher y al sistema
    WebSocket.
    """
    class Prioridad(models.TextChoices):
        """
        Prioridades de las notificaciones.
        """
        BAJA = "baja", "Baja"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name="notificaciones",)
    tipo = models.CharField(max_length=100)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    prioridad = models.CharField(max_length=20,choices=Prioridad.choices,default=Prioridad.MEDIA,)
    entidad_tipo = models.CharField(max_length=100,blank=True,)
    entidad_id = models.PositiveBigIntegerField(null=True,blank=True,)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True,)
    fecha_lectura = models.DateTimeField(null=True,blank=True,)

    class Meta:
        db_table = "notificacion"
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-fecha_creacion"]

        indexes = [
            models.Index(
                fields=["usuario", "-fecha_creacion"],
                name="notif_usuario_fecha_idx",
            ),
            models.Index(
                fields=["usuario", "leida"],
                name="notif_usuario_leida_idx",
            ),
            models.Index(
                fields=["entidad_tipo", "entidad_id"],
                name="notif_entidad_idx",
            ),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario}"