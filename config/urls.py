"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.auth.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Usuarios
    path('api/usuarios/', include('apps.usuarios.urls')),

    # Roles
    path('api/roles/', include('apps.roles.urls')),

    # Password Reset
    path('api/auth/', include('apps.auth.urls')),

    # JWT Authentication
    path('api/auth/login/', LoginView.as_view(), name='token_obtain_pair'), # Login con auditoría
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Swagger API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
