from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.inventory.models import Product
from apps.movements.models import Movement
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Productos con stock crítico
        context['low_stock_products'] = Product.objects.annotate(
            difference=models.F('min_stock') - models.F('current_stock')
        ).filter(current_stock__lt=models.F('min_stock'))[:10]
        
        # Estadísticas
        context['total_products'] = Product.objects.count()
        context['critical_stock'] = Product.objects.filter(
            current_stock__lt=models.F('min_stock')
        ).count()
        
        # Movimientos del día
        today = timezone.now().date()
        context['today_entries'] = Movement.objects.filter(
            movement_type='IN', 
            date__date=today
        ).count()
        
        context['today_exits'] = Movement.objects.filter(
            movement_type='OUT', 
            date__date=today
        ).count()
        
        return context
def request_replenishment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Lógica para manejar la solicitud
    # ...
    return redirect('inventory:list')  # Redirige a donde necesites