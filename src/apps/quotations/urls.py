from django.urls import path
from . import views

app_name = 'quotations'

urlpatterns = [
    path('', views.QuotationListView.as_view(), name='list'),
    path('nueva/', views.QuotationCreateView.as_view(), name='create'),
    path('<int:pk>/', views.QuotationDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', views.QuotationUpdateView.as_view(), name='update'),
    path('aprobar/<int:pk>/', views.approve_quotation, name='approve'),
    path('convertir/<int:pk>/', views.convert_to_order, name='convert'),
]