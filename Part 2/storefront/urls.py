"""
URL configuration for storefront project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from schema_graph.views import Schema

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

admin.site.site_header = "Storefront Ecommerce"
admin.site.index_title = "Admin Board"

urlpatterns = [
    path("admin/", admin.site.urls),
    # swagger api
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # model relation diagram
    path("diagrams", Schema.as_view(), name="model-diagram"),
    # playground
    path("playground", include("playground.urls")),
    # store
    path("api/v1/store", include("store.urls")),
    path("auth/", include("djoser.urls")),
    path("jwt-auth/", include("djoser.urls.jwt")),
]

if settings.DEBUG:
    urlpatterns.append(
        path("__debug__", include("debug_toolbar.urls"))
    )
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)