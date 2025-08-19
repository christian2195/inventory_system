from django.urls import path
from . import views
from .forms import MovementForm
app_name = 'movements'

urlpatterns = [
        path('', views.MovementListView.as_view(), name='list'),
    path('nuevo/', views.MovementCreateView.as_view(), name='create'),
    path('entradas/', views.EntryListView.as_view(), name='entry_list'),
    path('salidas/', views.ExitListView.as_view(), name='exit_list'),
]