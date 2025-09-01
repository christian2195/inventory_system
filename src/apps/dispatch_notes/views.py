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
from django.db.models import Q


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

    def post(self, request, *args, **kwargs):
        print("=== DEBUG CREATE POST ===")
        print("POST data keys:", list(request.POST.keys()))
        # No imprimir todo el POST porque puede ser muy largo
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        print("=== DEBUG FORM VALIDATION CREATE ===")
        print(f"Form is valid: {form.is_valid()}")
        print(f"Formset is valid: {formset.is_valid()}")
        
        if not form.is_valid():
            print("Form errors:", form.errors)
            
        if not formset.is_valid():
            print("Formset errors:", formset.errors)
            print("Formset non-form errors:", formset.non_form_errors())
            for i, item_form in enumerate(formset):
                if not item_form.is_valid():
                    print(f"Form {i} errors:", item_form.errors)
        
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
                    # COMENTA TEMPORALMENTE LA ACTUALIZACIÓN DE STOCK
                    # Product.objects.filter(pk=item.product.pk).update(current_stock=F('current_stock') - item.quantity)
                
                # Guarda los elementos eliminados
                for obj in formset.deleted_objects:
                    obj.delete()
                
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
            formset = DispatchItemFormSet(self.request.POST)
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
            context['formset'] = DispatchItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = DispatchItemFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        print("=== DEBUG UPDATE POST ===")
        print("POST data keys:", list(request.POST.keys()))
        
        self.object = self.get_object()
        form = self.get_form()
        formset = DispatchItemFormSet(self.request.POST, instance=self.object)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def form_valid(self, form, formset):
        print("=== DEBUG FORM VALIDATION UPDATE ===")
        print(f"Form is valid: {form.is_valid()}")
        print(f"Formset is valid: {formset.is_valid()}")
        
        if not form.is_valid():
            print("Form errors:", form.errors)
            
        if not formset.is_valid():
            print("Formset errors:", formset.errors)
            print("Formset non-form errors:", formset.non_form_errors())
            for i, item_form in enumerate(formset):
                if not item_form.is_valid():
                    print(f"Form {i} errors:", item_form.errors)
        
        with transaction.atomic():
            self.object = form.save()
            original_items = {item.pk: item for item in self.object.items.all()}
            updated_items = formset.save(commit=False)
            
            for item in updated_items:
                if item.pk:  # Item existente
                    original_item = original_items.get(item.pk)
                    if original_item:
                        # Si cambió el producto o la cantidad
                        if original_item.product != item.product:
                            # COMENTA TEMPORALMENTE STOCK
                            # Product.objects.filter(pk=original_item.product.pk).update(
                            #     current_stock=F('current_stock') + original_item.quantity
                            # )
                            # Product.objects.filter(pk=item.product.pk).update(
                            #     current_stock=F('current_stock') - item.quantity
                            # )
                            pass
                        elif original_item.quantity != item.quantity:
                            # COMENTA TEMPORALMENTE STOCK
                            # difference = original_item.quantity - item.quantity
                            # Product.objects.filter(pk=item.product.pk).update(
                            #     current_stock=F('current_stock') + difference
                            # )
                            pass
                else:  # Nuevo item
                    # COMENTA TEMPORALMENTE STOCK
                    # Product.objects.filter(pk=item.product.pk).update(
                    #     current_stock=F('current_stock') - item.quantity
                    # )
                    pass
                item.save()
            
            # Manejar items eliminados
            for item in formset.deleted_objects:
                # COMENTA TEMPORALMENTE STOCK
                # Product.objects.filter(pk=item.product.pk).update(
                #     current_stock=F('current_stock') + item.quantity
                # )
                item.delete()
            
            # Recalcular total
            self.object.total = sum(item.subtotal for item in self.object.items.all())
            self.object.save()
        
        messages.success(self.request, f"Nota de Despacho N°{self.object.dispatch_number} actualizada exitosamente.")
        return redirect(self.get_success_url())

    def form_invalid(self, form, formset):
        print("=== FORM INVALID ===")
        print(f"Form errors: {form.errors}")
        print(f"Formset errors: {formset.errors}")
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
    try:
        product_id = request.GET.get('id')
        query = request.GET.get('q', '')
        
        print(f"DEBUG API: id={product_id}, q={query}")
        
        if product_id:
            # VERIFICAR SI ES UN NÚMERO VÁLIDO
            try:
                product_id_int = int(product_id)
                products = Product.objects.filter(pk=product_id_int).values(
                    'id', 'product_code', 'description', 'unit_price', 'current_stock'
                )
            except (ValueError, TypeError):
                # Si no es un número, buscar por código de producto
                products = Product.objects.filter(
                    Q(product_code__iexact=product_id) | Q(description__icontains=product_id)
                ).values('id', 'product_code', 'description', 'unit_price', 'current_stock')[:1]
        
        elif query:
            # Búsqueda por texto
            products = Product.objects.filter(
                Q(product_code__icontains=query) | Q(description__icontains=query)
            ).values('id', 'product_code', 'description', 'unit_price', 'current_stock')[:10]
        else:
            products = Product.objects.none()
        
        products_list = list(products)
        print(f"DEBUG API: Returning {len(products_list)} products")
        return JsonResponse(products_list, safe=False)
        
    except Exception as e:
        print(f"ERROR in product_search_api: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def form_valid(self, form):
    context = self.get_context_data()
    formset = context['formset']
    
    print("=== DEBUG FORM VALIDATION CREATE ===")
    print(f"Form is valid: {form.is_valid()}")
    print(f"Formset is valid: {formset.is_valid()}")
    
    if not formset.is_valid():
        print("Formset errors:", formset.errors)
        print("Formset non-form errors:", formset.non_form_errors())
        
        # DEBUG DETALLADO DE CADA FORMULARIO
        for i, item_form in enumerate(formset):
            print(f"\n--- Form {i} ---")
            print(f"Is valid: {item_form.is_valid()}")
            print(f"Errors: {item_form.errors}")
            print(f"Non field errors: {item_form.non_field_errors()}")
            print(f"Data: {item_form.data}")
            print(f"Cleaned data: {getattr(item_form, 'cleaned_data', 'Not available')}")
            
            # Verificar campos específicos
            if 'product' in item_form.fields:
                print(f"Product field value: {item_form['product'].value()}")
            if 'quantity' in item_form.fields:
                print(f"Quantity field value: {item_form['quantity'].value()}")