from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from apps.dashboard.views import DashboardView
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Apps
    path('inventario/', include('apps.inventory.urls', namespace='inventory')),
    path('movimientos/', include('apps.movements.urls', namespace='movements')),
    path('despachos/', include('apps.dispatch_notes.urls', namespace='dispatch_notes')),
    path('cotizaciones/', include('apps.quotations.urls', namespace='quotations')),
    path('recepciones/', include('apps.reception_notes.urls', namespace='receptions')),
    path('devoluciones/', include('apps.returns.urls', namespace='returns')),
    
    path('404/', views.page_not_found, name='404'),
    
    # API
    path('api/', include([
        path('inventario/', include('apps.inventory.api_urls')),
        path('movimientos/', include('apps.movements.api_urls')),
    ])),
    
    # Error handlers
    path('404/', views.page_not_found, name='404'),
    path('500/', views.server_error, name='500'),
]

handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'
