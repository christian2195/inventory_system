from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import ReturnNote
from .forms import ReturnNoteForm
from movements.models import Movement
from dispatch_notes.models import DispatchItem

class ReturnNoteListView(LoginRequiredMixin, ListView):
    model = ReturnNote
    template_name = 'returns/return_list.html'
    context_object_name = 'returns'
    paginate_by = 15
    
    def get_queryset(self):
        return super().get_queryset().order_by('-return_date')

class ReturnNoteCreateView(LoginRequiredMixin, CreateView):
    model = ReturnNote
    form_class = ReturnNoteForm
    template_name = 'returns/return_form.html'
    success_url = reverse_lazy('returns')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return_note = form.save()
        
        # Registrar movimiento de entrada por devolución
        Movement.objects.create(
            product=return_note.product,
            movement_type='IN',
            quantity=return_note.quantity,
            unit_price=return_note.original_price,
            delivered_to=return_note.received_by,
            observations=f"Devolución #{return_note.return_number}",
            created_by=self.request.user
        )
        
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        if dispatch_item_id := self.request.GET.get('dispatch_item_id'):
            try:
                item = DispatchItem.objects.get(id=dispatch_item_id)
                initial['product'] = item.product
                initial['dispatch_note'] = item.dispatch_note
                initial['quantity'] = item.quantity
                initial['original_price'] = item.product.last_price
            except DispatchItem.DoesNotExist:
                pass
        return initial