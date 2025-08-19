from django.urls import path
from . import views

app_name = 'returns'

urlpatterns = [
    path('', views.ReturnNoteListView.as_view(), name='list'),
    path('nueva/', views.ReturnNoteCreateView.as_view(), name='create'),
    path('por-despacho/<int:dispatch_id>/', views.create_from_dispatch, name='create_from_dispatch'),
    path('<int:pk>/', views.ReturnNoteDetailView.as_view(), name='detail'),
    path('procesar/<int:pk>/', views.process_return, name='process'),
]