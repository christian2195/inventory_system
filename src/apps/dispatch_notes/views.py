# src/apps/dispatch_notes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import DispatchNote, DispatchItem
from .forms import DispatchNoteForm, DispatchItemFormSet
from apps.inventory.models import Product  # Eliminada la importación de Brand
from django.db.models import F
from django.contrib import messages

# Vistas de la interfaz de usuario
class DispatchNoteListView(LoginRequiredMixin, ListView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_list.html'
    context_object_name = 'dispatches'
    paginate_by = 15
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('items').order_by('-dispatch_date')

class DispatchNoteCreateView(LoginRequiredMixin, CreateView):
    model = DispatchNote
    form_class = DispatchNoteForm
    template_name = 'dispatch_notes/dispatch_form.html'
    success_url = reverse_lazy('dispatch_notes:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in context:
            context['formset'] = DispatchItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object.save()

            if formset.is_valid():
                formset.instance = self.object
                items_to_save = formset.save(commit=False)
                for item in items_to_save:
                    # El campo product_search es temporal, obtén el producto real del ID
                    product_id = self.request.POST.get(f'dispatchitem_set-{item.id}-product')
                    item.product_id = product_id
                    item.subtotal = item.quantity * (item.unit_price if item.unit_price else 0)
                    item.save()
                    Product.objects.filter(pk=item.product.pk).update(current_stock=F('current_stock') - item.quantity)
                
                # Maneja la relación ManyToMany
                formset.save_m2m()
                
                total = sum(item.subtotal for item in self.object.items.all())
                self.object.total = total
                self.object.save()
            else:
                messages.error(self.request, "Hubo un error con los productos. Por favor, revisa los datos ingresados.")
                return self.form_invalid(form, formset)
        
        messages.success(self.request, f"Nota de Despacho N°{self.object.dispatch_number} creada exitosamente.")
        return redirect(self.get_success_url())
    
    def form_invalid(self, form, formset=None):
        if formset is None:
            formset = DispatchItemFormSet(self.request.POST, instance=self.object)
        context = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(context)

# ... (El resto de tus vistas de detalle y actualización, no requieren cambios mayores) ...
# Asegúrate de que las vistas de detalle y actualización también manejen el nuevo campo product_search

def product_search_api(request):
    query = request.GET.get('q', '')
    if len(query) < 3:
        return JsonResponse({'results': []})

    products = Product.objects.filter(code__icontains=query) | Product.objects.filter(description__icontains=query)
    
    results = [
        {
            'id': p.id,
            'text': f"{p.code} - {p.description}",
            'stock': p.current_stock,
            'price': float(p.unit_price),
            'brand': p.brand,  # Accede directamente al campo CharField
            'model': p.model if p.model else '',
        } for p in products[:10]  # Se eliminó select_related
    ]
    return JsonResponse({'results': results})