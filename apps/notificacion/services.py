from django.utils import timezone

from apps.notificacion.models import Notificacion


def crear_notificacion(
    *,
    usuario,
    tipo,
    titulo,
    mensaje,
    prioridad=Notificacion.Prioridad.MEDIA,
    entidad=None,
):
    """
    Crea una notificación para un usuario.

    Se usa cuando ocurre un evento del sistema que el usuario
    necesita conocer.

    Ejemplo:
        crear_notificacion(
            usuario=usuario,
            tipo="USUARIO_ROL_ASIGNADO",
            titulo="Rol asignado",
            mensaje="Se te ha asignado el rol Supervisor.",
            entidad=usuario,
        )
    """

    entidad_tipo = ""
    entidad_id = None

    if entidad is not None:
        if entidad.pk is None:
            raise ValueError(
                "La entidad debe estar guardada antes de crear la notificación."
            )

        entidad_tipo = entidad._meta.label_lower
        entidad_id = entidad.pk

    return Notificacion.objects.create(
        usuario=usuario,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        prioridad=prioridad,
        entidad_tipo=entidad_tipo,
        entidad_id=entidad_id,
    )


def crear_notificaciones(
    *,
    usuarios,
    tipo,
    titulo,
    mensaje,
    prioridad=Notificacion.Prioridad.MEDIA,
    entidad=None,
):
    """
    Crea la misma notificación para varios usuarios.

    Se usa cuando un mismo evento debe informar a varias personas.

    Ejemplo:
        crear_notificaciones(
            usuarios=supervisores,
            tipo="CALIDAD_LOTE_RECHAZADO",
            titulo="Lote rechazado",
            mensaje="El lote LOT-452 fue rechazado.",
            prioridad=Notificacion.Prioridad.ALTA,
            entidad=lote,
        )
    """

    entidad_tipo = ""
    entidad_id = None

    if entidad is not None:
        if entidad.pk is None:
            raise ValueError(
                "La entidad debe estar guardada antes de crear las notificaciones."
            )

        entidad_tipo = entidad._meta.label_lower
        entidad_id = entidad.pk

    notificaciones = [
        Notificacion(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            prioridad=prioridad,
            entidad_tipo=entidad_tipo,
            entidad_id=entidad_id,
        )
        for usuario in usuarios
    ]

    return Notificacion.objects.bulk_create(notificaciones)


def marcar_como_leida(*, usuario, notificacion_id):
    """
    Marca una notificación como leída.

    Solo puede hacerlo el usuario propietario de la notificación.

    Ejemplo:
        marcar_como_leida(
            usuario=request.user,
            notificacion_id=15,
        )
    """

    notificacion = Notificacion.objects.get(
        id=notificacion_id,
        usuario=usuario,
    )

    if notificacion.leida:
        return notificacion

    notificacion.leida = True
    notificacion.fecha_lectura = timezone.now()

    notificacion.save(
        update_fields=[
            "leida",
            "fecha_lectura",
        ]
    )

    return notificacion


def marcar_todas_como_leidas(*, usuario):
    """
    Marca como leídas todas las notificaciones pendientes de un usuario.

    Se usa para acciones como "Marcar todas como leídas".

    Ejemplo:
        marcar_todas_como_leidas(usuario=request.user)
    """

    fecha_lectura = timezone.now()

    return Notificacion.objects.filter(
        usuario=usuario,
        leida=False,
    ).update(
        leida=True,
        fecha_lectura=fecha_lectura,
    )


def contar_no_leidas(*, usuario):
    """
    Obtiene cuántas notificaciones pendientes tiene un usuario.

    Se usa para mostrar el contador de notificaciones en el frontend.

    Ejemplo:
        cantidad = contar_no_leidas(usuario=request.user)
    """

    return Notificacion.objects.filter(
        usuario=usuario,
        leida=False,
    ).count()