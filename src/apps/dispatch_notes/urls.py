from django.urls import path
from . import views

app_name = 'dispatch_notes'

urlpatterns = [
    path('', views.DispatchNoteListView.as_view(), name='list'),
    path('nuevo/', views.DispatchNoteCreateView.as_view(), name='create'),
    path('<int:pk>/', views.DispatchNoteDetailView.as_view(), name='detail'),
    path('editar/<int:pk>/', views.DispatchNoteUpdateView.as_view(), name='update'),
    path('imprimir/<int:pk>/', views.DispatchNotePrintView.as_view(), name='print'),
    path('buscar-productos/', views.product_search_api, name='product_search'),
]