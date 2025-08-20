# src/apps/reception_notes/views.py
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import ReceptionNote, ReceptionItem
from .forms import ReceptionNoteForm, ReceptionItemFormSet
from apps.inventory.models import Product, Supplier
from apps.movements.models import Movement
from apps.orders.models import Order, OrderItem
from django.views.generic import TemplateView
from django.db.models import Count, F, Q
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
    success_url = reverse_lazy('receptions:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ReceptionItemFormSet(self.request.POST)
        else:
            context['formset'] = ReceptionItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.received_by = self.request.user
            self.object.save()

            if formset.is_valid():
                formset.instance = self.object
                formset.save()

                for item in self.object.items.all():
                    Movement.objects.create(
                        product=item.product,
                        movement_type='IN',
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        delivered_to=self.object.received_by,
                        observations=f"Recepción #{self.object.reception_number}",
                        created_by=self.request.user
                    )
            else:
                return self.form_invalid(form)

        return super().form_valid(form)

class ReceptionNoteDetailView(LoginRequiredMixin, DetailView):
    model = ReceptionNote
    template_name = 'reception_notes/reception_detail.html'
    context_object_name = 'reception'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context

@transaction.atomic
def validate_reception(request, pk):
    reception = get_object_or_404(ReceptionNote, pk=pk)
    reception.status = 'VALIDATED'
    reception.save()
    messages.success(request, 'Nota de recepción validada con éxito.')
    return redirect('receptions:detail', pk=pk)

@transaction.atomic
def create_from_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        reception = ReceptionNote.objects.create(
            supplier=order.supplier,
            received_by=request.user,
            reception_number=f'REC-{order.order_number}',
            notes=f'Creada automáticamente desde Orden de Compra #{order.order_number}'
        )

        for item in order.items.all():
            ReceptionItem.objects.create(
                reception_note=reception,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price
            )

        messages.success(request, 'Nota de recepción creada desde la orden de compra con éxito.')
        return redirect('receptions:detail', pk=reception.pk)

    context = {
        'order': order,
    }
    return render(request, 'reception_notes/create_from_order_confirm.html', context)