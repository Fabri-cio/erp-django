from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notificacion.models import Notificacion
from apps.notificacion.serializers import NotificacionSerializer
from apps.notificacion.services import (
    contar_no_leidas,
    marcar_como_leida,
    marcar_todas_como_leidas,
)


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoints para consultar y gestionar las notificaciones
    del usuario autenticado.

    La app de notificaciones es agnóstica respecto a los módulos
    de negocio. Los módulos de negocio son responsables de decidir
    cuándo se debe crear una notificación y quién debe recibirla.

    Este ViewSet permite:

    - Consultar las notificaciones propias.
    - Consultar una notificación específica.
    - Marcar una notificación como leída.
    - Marcar todas las notificaciones como leídas.
    - Consultar la cantidad de notificaciones no leídas.

    No permite crear, modificar ni eliminar notificaciones
    directamente mediante la API. Las notificaciones deben ser
    creadas desde los servicios de la aplicación.
    """

    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    # Las notificaciones no necesitan filtros ni ordenamiento
    # configurables desde el frontend.
    #
    # Se desactivan explícitamente porque DRF puede heredar
    # los filter_backends definidos globalmente en settings.py.
    filter_backends = []

    # La lista siempre se muestra de la más reciente
    # a la más antigua.
    ordering = ["-fecha_creacion"]

    def get_queryset(self):
        """
        Devuelve únicamente las notificaciones del usuario autenticado.

        Esta restricción es importante porque una notificación pertenece
        a un usuario específico y no debe poder ser consultada por otro.
        """
        return Notificacion.objects.filter(
            usuario=self.request.user,
        ).order_by("-fecha_creacion")

    @action(
        detail=True,
        methods=["post"],
        url_path="marcar-leida",
    )
    def marcar_leida(self, request, pk=None):
        """
        Marca una notificación específica como leída.

        Solo puede marcarse como leída una notificación perteneciente
        al usuario autenticado.
        """
        try:
            notificacion = marcar_como_leida(
                usuario=request.user,
                notificacion_id=pk,
            )
        except Notificacion.DoesNotExist:
            return Response(
                {"detail": "La notificación no existe."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(notificacion)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="marcar-todas-leidas",
    )
    def marcar_todas_leidas(self, request):
        """
        Marca como leídas todas las notificaciones pendientes
        del usuario autenticado.
        """
        cantidad = marcar_todas_como_leidas(
            usuario=request.user,
        )

        return Response(
            {"actualizadas": cantidad},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="contador-no-leidas",
    )
    def contador_no_leidas(self, request):
        """
        Devuelve la cantidad de notificaciones no leídas
        del usuario autenticado.
        """
        cantidad = contar_no_leidas(
            usuario=request.user,
        )

        return Response(
            {"no_leidas": cantidad},
            status=status.HTTP_200_OK,
        )