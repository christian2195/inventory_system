# src/apps/dispatch_notes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db import transaction
from .models import DispatchNote, DispatchItem
from .forms import DispatchNoteForm, DispatchItemFormSet
from apps.inventory.models import Product

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
        if self.request.POST:
            context['formset'] = DispatchItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DispatchItemFormSet(instance=self.object)
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
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.dispatch_note = self.object
                    instance.save()
                
                    # Actualizar stock del producto
                    product = instance.product
                    product.current_stock -= instance.quantity
                    product.save()
            else:
                return self.form_invalid(form)
            
        return redirect(self.get_success_url())
class DispatchNoteDetailView(LoginRequiredMixin, DetailView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_detail.html'
    context_object_name = 'dispatch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product')
        return context

class DispatchNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = DispatchNote
    form_class = DispatchNoteForm
    template_name = 'dispatch_notes/dispatch_form.html'
    success_url = reverse_lazy('dispatch_notes:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DispatchItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DispatchItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            self.object = form.save()
            
            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                return self.form_invalid(form)
            
        return redirect(self.get_success_url())

class DispatchNotePrintView(LoginRequiredMixin, DetailView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_print.html'
    context_object_name = 'dispatch'
    
# Vista para API de búsqueda de productos
def product_search_api(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(code__icontains=query) | Product.objects.filter(description__icontains=query)
    results = [{'id': p.id, 'text': f"{p.code} - {p.description}"} for p in products]
    return JsonResponse({'results': results})