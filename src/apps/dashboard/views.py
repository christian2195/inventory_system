from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.inventory.models import Product
from apps.movements.models import Movement
from django.db.models import F
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Productos con stock crítico
        context['low_stock_products'] = Product.objects.get_low_stock_products()
        
        # Estadísticas
        context['total_products'] = Product.objects.count()
        context['critical_stock'] = Product.objects.filter(
            current_stock__lt=F('min_stock')
        ).count()
        
        # Movimientos del día
        context['today_entries'] = Movement.objects.get_daily_movements('IN')
        context['today_exits'] = Movement.objects.get_daily_movements('OUT')
        
        return context

# La función request_replenishment queda igual
def request_replenishment(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Lógica para manejar la solicitud
    # ...
    return redirect('dashboard')