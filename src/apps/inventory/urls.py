from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductCreateView,
    ProductUpdateView,
    InventoryReportView,
    request_replenishment  # Asegúrate que existe en views.py
)
app_name = 'inventory'

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('nuevo/', ProductCreateView.as_view(), name='create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', ProductUpdateView.as_view(), name='update'),
    path('reporte/', InventoryReportView.as_view(), name='report'),
    path('solicitar/<int:pk>/', request_replenishment, name='request'),
    # Eliminé el path duplicado de 'report/'
]