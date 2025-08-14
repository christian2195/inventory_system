from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Productos
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Movimientos
    path('movements/', views.MovementListView.as_view(), name='movement_list'),
    path('movements/add/', views.MovementCreateView.as_view(), name='movement_add'),
    path('movements/<int:pk>/', views.MovementDetailView.as_view(), name='movement_detail'),
    
    # Reportes
    path('reports/', views.generate_report, name='generate_report'),
    
    # Importar/Exportar
    path('import-export/', views.import_data, name='import_export'),
    path('export/', views.export_data, name='export_data'),
]