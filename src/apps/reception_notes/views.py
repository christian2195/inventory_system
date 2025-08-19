from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import ReceptionNote
from .forms import ReceptionNoteForm
from movements.models import Movement
from django.utils import timezone

class ReceptionNoteListView(LoginRequiredMixin, ListView):
    model = ReceptionNote
    template_name = 'reception_notes/reception_list.html'
    context_object_name = 'receptions'
    paginate_by = 15
    
    def get_queryset(self):
        return super().get_queryset().order_by('-reception_date')

class ReceptionNoteCreateView(LoginRequiredMixin, CreateView):
    model = ReceptionNote
    form_class = ReceptionNoteForm
    template_name = 'reception_notes/reception_form.html'
    success_url = reverse_lazy('receptions')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        reception = form.save()
        
        # Registrar movimiento de entrada para cada producto
        for item in reception.items.all():
            Movement.objects.create(
                product=item.product,
                movement_type='IN',
                quantity=item.quantity,
                unit_price=item.unit_price,
                delivered_to=reception.received_by,
                observations=f"Recepción #{reception.reception_number}",
                created_by=self.request.user
            )
        
        return super().form_valid(form)