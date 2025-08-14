# inventory_system/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='inventory/', permanent=True)), # <-- Añade esta línea
    path('admin/', admin.site.urls),
    path('inventory/', include('inventory.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]