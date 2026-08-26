from django.contrib import admin

from .models import Auditoria

# Registro del modelo Auditoria en el admin
@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "usuario",
        "accion",
        "metodo",
        "endpoint",
        "ip",
        "detalle",
        "fecha",
    ]

    list_filter = [
        "metodo",
        "accion",
        "fecha",
    ]

    search_fields = [
        "usuario__username",
        "endpoint",
        "accion",
        "ip",
        "detalle",
    ]

    ordering = [
        "-fecha",
    ]