from rest_framework.routers import DefaultRouter

from apps.notificacion.views import NotificacionViewSet


router = DefaultRouter()

router.register(
    r"",
    NotificacionViewSet,
    basename="notificacion",
)

urlpatterns = router.urls