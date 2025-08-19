from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import ReceptionNote
from .forms import ReceptionNoteForm
from movements.models import Movement
from django.utils import timezone

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.now().date()

        # Combinar consultas de estadísticas en una sola
        product_stats = Product.objects.aggregate(
            total_products=Count('id'),
            critical_stock=Count('id', filter=Q(current_stock__lt=F('min_stock')))
        )

        context.update(product_stats)

        # Combinar consultas de movimientos en una sola
        movement_stats = Movement.objects.filter(
            date__date=today
        ).aggregate(
            today_entries=Count('id', filter=Q(movement_type='IN')),
            today_exits=Count('id', filter=Q(movement_type='OUT'))
        )

        context.update(movement_stats)

        # Consulta para productos con stock crítico (puede mantenerse separada para la lista)
        context['low_stock_products'] = Product.objects.filter(
            current_stock__lt=F('min_stock')
        ).annotate(
            difference=F('min_stock') - F('current_stock')
        ).order_by('difference')[:10]

        return context
    
def request_replenishment(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        # Crea una nueva solicitud de reabastecimiento
        Request.objects.create(
            product=product,
            requested_by=request.user,
            # ... otros campos
        )
        messages.success(request, 'Solicitud de reabastecimiento enviada con éxito.')
        return redirect('dashboard:index') # O a otra URL
    return redirect('dashboard:index')