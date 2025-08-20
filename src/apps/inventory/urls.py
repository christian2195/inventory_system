# src/apps/inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='inventory_dashboard'),
    path('', views.ProductListView.as_view(), name='list'),
    path('nuevo/', views.ProductCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', views.ProductUpdateView.as_view(), name='update'),
    path('reporte/', views.InventoryReportView.as_view(), name='report'),
    path('solicitar/<int:pk>/', views.request_replenishment, name='request'),
]