from django.urls import path
from rest_framework import routers
from . import api_views

router = routers.DefaultRouter()
router.register(r'productos', api_views.ProductViewSet)
router.register(r'proveedores', api_views.SupplierViewSet)

urlpatterns = [
    path('stock/', api_views.StockAPIView.as_view(), name='stock'),
    path('productos/buscar/', api_views.ProductSearchAPI.as_view(), name='product_search'),
    path('alertas-stock/', api_views.StockAlertsAPI.as_view(), name='stock_alerts'),
] + router.urls