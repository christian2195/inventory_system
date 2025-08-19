from django.urls import path
from . import views

app_name = 'receptions'

urlpatterns = [
    path('', views.ReceptionNoteListView.as_view(), name='list'),
    path('nueva/', views.ReceptionNoteCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ReceptionNoteDetailView.as_view(), name='detail'),
    path('validar/<int:pk>/', views.validate_reception, name='validate'),
    path('asociar-orden/<int:order_id>/', views.create_from_order, name='create_from_order'),
]