from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import DispatchNote, DispatchItem
from .forms import DispatchNoteForm, DispatchItemFormSet
from inventory.models import Product

class DispatchNoteListView(LoginRequiredMixin, ListView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_list.html'
    context_object_name = 'dispatches'
    paginate_by = 15
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('items').order_by('-dispatch_date')

class DispatchNoteDetailView(LoginRequiredMixin, DetailView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_detail.html'
    context_object_name = 'dispatch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product')
        return context

class DispatchNoteCreateView(LoginRequiredMixin, CreateView):
    model = DispatchNote
    form_class = DispatchNoteForm
    template_name = 'dispatch_notes/dispatch_form.html'
    success_url = reverse_lazy('dispatch_notes')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DispatchItemFormSet(self.request.POST)
        else:
            context['formset'] = DispatchItemFormSet(queryset=DispatchItem.objects.none())
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object.save()
            
            # Guardar items
            instances = formset.save(commit=False)
            for instance in instances:
                instance.dispatch_note = self.object
                instance.save()
                
                # Actualizar stock del producto
                product = instance.product
                product.current_stock -= instance.quantity
                product.save()
            
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))