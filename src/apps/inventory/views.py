from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, F
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Supplier, Warehouse
from apps.inventory.forms import ProductForm

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(code__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(supplier__name__icontains=search_query)
            )
            
        return queryset.select_related('supplier', 'warehouse')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movements'] = self.object.movement_set.order_by('-date')[:10]
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory')

class InventoryReportView(ListView):
    model = Product
    template_name = 'inventory/report.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        # Filtra para obtener productos con stock crítico
        return Product.objects.annotate(
            stock_difference=F('min_stock') - F('current_stock')
        ).filter(current_stock__lt=F('min_stock')).order_by('-stock_difference')

def request_replenishment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Lógica para manejar la solicitud de reposición
    # Por ejemplo, podrías crear un registro de un movimiento especial,
    # enviar un correo electrónico al proveedor o registrar una alerta.
    
    # Aquí puedes añadir la lógica de negocio real.
    # Por ejemplo:
    # new_movement = Movement.objects.create(
    #     product=product,
    #     quantity=product.min_stock - product.current_stock,
    #     movement_type='REQUEST'
    # )
    
    # Redireccionar de vuelta a la página del producto
    return redirect('inventory:detail', pk=product.pk)