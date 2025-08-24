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
from apps.inventory.models import Product
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
                    item.subtotal = item.quantity * (item.unit_price if item.unit_price else 0)
                    item.save()
                    Product.objects.filter(pk=item.product.pk).update(current_stock=F('current_stock') - item.quantity)
                
                # Guarda los elementos eliminados
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

class DispatchNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = DispatchNote
    form_class = DispatchNoteForm
    template_name = 'dispatch_notes/dispatch_form.html'
    success_url = reverse_lazy('dispatch_notes:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = DispatchItemFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['formset'] = DispatchItemFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        # Guardar la nota antes de procesar los items
        with transaction.atomic():
            self.object = form.save()
            
            if formset.is_valid():
                # Obtener una copia de los items originales antes de guardar los nuevos cambios
                original_items = {item.pk: item for item in self.object.items.all()}
                
                # Guarda los cambios en el formset
                instances = formset.save(commit=False)
                
                # Procesa los elementos modificados y nuevos
                for instance in instances:
                    # Actualiza el subtotal
                    instance.subtotal = instance.quantity * (instance.unit_price if instance.unit_price else 0)
                    
                    # Si es un item nuevo, guardar y ajustar stock
                    if instance.pk is None:
                        instance.save()
                        Product.objects.filter(pk=instance.product.pk).update(current_stock=F('current_stock') - instance.quantity)
                    else:
                        # Si es un item modificado, recalcular el cambio de stock
                        old_item = original_items[instance.pk]
                        stock_change = old_item.quantity - instance.quantity
                        
                        # Guardar el item
                        instance.save()
                        
                        # Si el producto es el mismo, ajustar el stock por la diferencia
                        if old_item.product.pk == instance.product.pk:
                            Product.objects.filter(pk=instance.product.pk).update(current_stock=F('current_stock') + stock_change)
                        # Si el producto ha cambiado, ajustar ambos stocks
                        else:
                            Product.objects.filter(pk=old_item.product.pk).update(current_stock=F('current_stock') + old_item.quantity)
                            Product.objects.filter(pk=instance.product.pk).update(current_stock=F('current_stock') - instance.quantity)
                
                # Procesa los elementos eliminados
                for item in formset.deleted_objects:
                    Product.objects.filter(pk=item.product.pk).update(current_stock=F('current_stock') + item.quantity)
                    item.delete()

                # Recalcular el total después de todos los cambios
                self.object.total = sum(item.subtotal for item in self.object.items.all())
                self.object.save()
            else:
                messages.error(self.request, "Hubo un error con los productos. Por favor, revisa los datos ingresados.")
                return self.form_invalid(form, formset)

        messages.success(self.request, f"Nota de Despacho N°{self.object.dispatch_number} actualizada exitosamente.")
        return redirect(self.get_success_url())

    def form_invalid(self, form, formset=None):
        if formset is None:
            formset = DispatchItemFormSet(self.request.POST, instance=self.object)
        context = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(context)
    
    
class DispatchNoteDetailView(LoginRequiredMixin, DetailView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_detail.html'
    context_object_name = 'dispatch_note'
    
    def get_queryset(self):
        return super().get_queryset().select_related('client', 'created_by').prefetch_related('items__product')
    
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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = DispatchItemFormSet(self.request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        with transaction.atomic():
            # 1. Guardar la nota de despacho principal
            self.object = form.save()
            
            # 2. Obtener los productos originales para calcular el cambio de stock
            original_items = {item.pk: item for item in self.object.items.all()}
            
            # 3. Guardar los items del formset (nuevos y modificados)
            updated_items = formset.save(commit=False)
            
            for item in updated_items:
                if item.pk in original_items:
                    original_item = original_items.pop(item.pk)
                    change = original_item.quantity - item.quantity
                    if change != 0:
                        Product.objects.filter(pk=item.product.pk).update(current_stock=F('current_stock') + change)
                item.save()

            # 4. Manejar los items eliminados
            for item in formset.deleted_objects:
                Product.objects.filter(pk=item.product.pk).update(current_stock=F('current_stock') + item.quantity)
                item.delete()

            # 5. Calcular y guardar el total de la nota
            total = sum(item.subtotal for item in self.object.items.all())
            self.object.total = total
            self.object.save()

        return redirect(self.get_success_url())

    def form_invalid(self, form, formset):
        context = self.get_context_data(form=form, formset=formset)
        return self.render_to_response(context)
    
class DispatchNotePrintView(LoginRequiredMixin, DetailView):
    model = DispatchNote
    template_name = 'dispatch_notes/dispatch_print.html'
    context_object_name = 'dispatch'
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        
        html_string = render_to_string(self.template_name, context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="nota_despacho_{self.object.dispatch_number}.pdf"'
        
        return response
    
def product_search_api(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(code__icontains=query) | Product.objects.filter(description__icontains=query)
    results = [{'id': p.id, 'text': f"{p.code} - {p.description}"} for p in products]
    return JsonResponse({'results': results})