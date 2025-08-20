# src/apps/inventory/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from .models import Product, Supplier, Client, Warehouse
from .forms import ProductForm
from django.db.models import F
from django.contrib import messages
from django.db.models.functions import Lower
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

# Vistas de la aplicación web (no API)

def dashboard_view(request):
    low_stock_products_count = Product.objects.filter(current_stock__lte=F('min_stock')).count()
    context = {
        'low_stock_products_count': low_stock_products_count
    }
    return render(request, 'inventory/dashboard.html', context)

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'inventory/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by(Lower('description'))
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(description__icontains=query)
        return queryset

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'inventory/product_detail.html'
    context_object_name = 'product'

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:list')

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'inventory/product_form.html'
    success_url = reverse_lazy('inventory:list')

class InventoryReportView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/report.html'

@login_required
def request_replenishment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Aquí puedes añadir la lógica para notificar, enviar un email, etc.
    messages.success(request, f'Solicitud de reabastecimiento para "{product.description}" enviada con éxito.')
    return redirect('inventory:detail', pk=product.pk)