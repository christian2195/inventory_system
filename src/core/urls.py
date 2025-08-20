# src/core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # URLs de autenticación de usuario
    path('accounts/', include('apps.users.urls')),
    
    # URLs de la API
    path('api/inventario/', include('apps.inventory.api_urls')),
    path('api/movimientos/', include('apps.movements.api_urls')),
    path('api/cotizaciones/', include('apps.quotations.api_urls')),
    path('api/notas-recepcion/', include('apps.reception_notes.api_urls')),

    # URLs de la aplicación web
    path('inventario/', include('apps.inventory.urls')),
    path('cotizaciones/', include('apps.quotations.urls')),
    # URLs de utilidades y error
    path('admin/', admin.site.urls),
    path('404/', views.page_not_found, name='404'),
    path('500/', views.server_error, name='500'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
