# src/apps/reception_notes/urls.py
from django.urls import path
from . import views

app_name = 'reception_notes'

urlpatterns = [
    path('', views.ReceptionNoteListView.as_view(), name='list'),
    path('nuevo/', views.ReceptionNoteCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ReceptionNoteDetailView.as_view(), name='detail'),
    path('<int:pk>/validar/', views.validate_reception, name='validate'),
    path('crear-desde-orden/<int:order_id>/', views.create_from_order, name='create_from_order'),
]