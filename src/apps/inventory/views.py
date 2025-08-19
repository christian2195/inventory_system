from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
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
    template_name = 'inventory/report.html'  # Asegúrate de crear esta plantilla
    context_object_name = 'products'
    
    def get_queryset(self):
        # Personaliza el queryset si es necesario
        return Product.objects.filter(...)

def request_replenishment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Aquí va tu lógica para manejar la solicitud
    # Por ejemplo:
    # product.request_replenishment()
    # return redirect('inventory:detail', pk=product.pk)
    return redirect('inventory:list')  # Cambia esto por tu lógica real