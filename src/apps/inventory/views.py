# src/apps/inventory/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Product
from .forms import ProductForm
from django.db.models import F
from django.contrib import messages
from django.db.models.functions import Lower
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.views import View

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

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'inventory/product_confirm_delete.html'
    success_url = reverse_lazy('inventory:list')

class InventoryReportView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory/report.html'

class InventoryReportPDFView(LoginRequiredMixin, View):
    """Vista básica para reporte PDF"""
    
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        
        html_string = render_to_string('inventory/report_pdf.html', {
            'products': products
        })
        
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="inventory_report.pdf"'
        return response
    
@login_required
def request_replenishment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Implement actual notification logic
    try:
        # Example: Send email notification
        subject = f"Replenishment Request: {product.description}"
        message = f"Product {product.description} (SKU: {product.sku}) needs replenishment.\nCurrent stock: {product.current_stock}\nMinimum stock: {product.min_stock}"
        
        # Replace with your actual email sending logic
        # send_mail(subject, message, 'noreply@example.com', ['inventory@example.com'])
        
        messages.success(request, f'Solicitud de reabastecimiento para "{product.description}" enviada con éxito.')
    except Exception as e:
        messages.error(request, f'Error al enviar la solicitud: {str(e)}')
    
    return redirect('inventory:detail', pk=product.pk)