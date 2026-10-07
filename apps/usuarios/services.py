from django.contrib.auth import get_user_model
from django.db import transaction

from apps.notificacion.models import Notificacion
from apps.notificacion.services import crear_notificaciones


Usuario = get_user_model()


@transaction.atomic
def asignar_roles_a_usuario(*, actor, usuario, roles):
    """
    Asigna uno o varios roles a un usuario y genera las
    notificaciones correspondientes.

    Este servicio representa el caso de uso completo de
    asignación de roles. La vista no debe contener la lógica
    de negocio relacionada con la operación.

    Responsabilidades:
        1. Recibir quién realiza la acción (`actor`).
        2. Recibir el usuario al que se asignarán los roles.
        3. Asignar los roles al usuario.
        4. Determinar los administradores activos que deben
           recibir la notificación.
        5. Crear las notificaciones mediante la aplicación
           `notificacion`.

    La aplicación `notificacion` permanece agnóstica respecto
    al contexto de usuarios. Este servicio es quien conoce
    la regla de negocio de que los administradores activos
    deben ser notificados cuando se asignan roles.

    La operación está protegida mediante `transaction.atomic`.
    Si ocurre un error durante la asignación o durante la
    creación de las notificaciones, los cambios realizados
    dentro de esta operación se revierten.

    Args:
        actor:
            Usuario que realiza la operación.

        usuario:
            Usuario al que se le asignarán los roles.

        roles:
            Iterable de objetos Group que representan los roles
            que deben asignarse.

    Returns:
        list:
            Lista de roles asignados.

    Raises:
        Exception:
            Cualquier excepción producida durante la operación
            provoca el rollback de la transacción.

    Example:
        asignar_roles_a_usuario(
            actor=request.user,
            usuario=usuario,
            roles=roles,
        )
    """

    # Convertimos el iterable a lista para poder reutilizar
    # los roles posteriormente al construir la respuesta o
    # la notificación.
    roles = list(roles)

    # Asignamos los roles al usuario.
    usuario.groups.add(*roles)

    # Los destinatarios de la notificación pertenecen a la
    # regla de negocio del módulo usuarios.
    administradores = (
        Usuario.objects
        .filter(
            is_active=True,
            groups__name="admin", # Es el nombre del rol en la base de datos
        )
        .exclude(
            id=actor.id,
        )
        .distinct()
    )

    nombres_roles = ", ".join(
        role.name
        for role in roles
    )

    crear_notificaciones(
        usuarios=administradores,
        tipo="usuarios.roles_asignados",
        titulo="Roles asignados",
        mensaje=(
            f"Se asignaron los roles "
            f"{nombres_roles} al usuario "
            f"{usuario.username}."
        ),
        prioridad=Notificacion.Prioridad.MEDIA,
        entidad=usuario,
    )

    return roles