# src/apps/movements/views.py
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Movement, Entry  # Clean single import
from apps.inventory.models import Product
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta
from .models import Movement
from django.forms import inlineformset_factory
from .models import DispatchNote, DispatchItem
from .forms import DispatchNoteForm, DispatchItemForm


class MovementListView(LoginRequiredMixin, ListView):
    model = Movement
    template_name = 'movements/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('product', 'product__supplier')
        movement_type = self.request.GET.get('type')
        
        if movement_type == 'entrada':
            queryset = queryset.filter(movement_type='IN')
        elif movement_type == 'salida':
            queryset = queryset.filter(movement_type='OUT')
            
        return queryset.order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movement_type'] = self.request.GET.get('type', '')
        return context

class MovementCreateView(LoginRequiredMixin, CreateView):
    model = Movement
    form_class = MovementForm
    template_name = 'movements/movement_form.html'
    success_url = reverse_lazy('movements')
    
    def get_initial(self):
        initial = super().get_initial()
        if product_id := self.request.GET.get('product_id'):
            try:
                product = Product.objects.get(id=product_id)
                initial['product'] = product
                initial['unit_price'] = product.last_price if product.last_price else 0
            except Product.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        movement = form.save()
        
        # Actualizar último precio en el producto
        product = movement.product
        product.last_price = movement.unit_price
        product.save()
        
        return super().form_valid(form)

class EntryListView(ListView):
    model = Entry
    template_name = 'movements/entry_list.html'  # Verify this template exists
    context_object_name = 'entries'

class ExitListView(ListView):
    model = Movement
    template_name = 'movements/exit_list.html'
    context_object_name = 'exits'
    
    def get_queryset(self):
        return super().get_queryset().filter(movement_type='OUT').order_by('-date')

class MonthlyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'movements/monthly_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate date range (last 30 days)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Get movements in date range
        movements = Movement.objects.filter(
            date__range=(start_date, end_date)
        ).select_related('product')
        
        # Add to context
        context['movements'] = movements
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        return context