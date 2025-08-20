# src/apps/returns/views.py
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import ReturnNote, ReturnItem
from .forms import ReturnNoteForm, ReturnItemFormSet
from apps.inventory.models import Product, Client
from apps.dispatch_notes.models import DispatchNote, DispatchItem
from apps.movements.models import Movement
from django.db.models import F

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
    success_url = reverse_lazy('returns:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ReturnItemFormSet(self.request.POST)
        else:
            context['formset'] = ReturnItemFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.returned_by = self.request.user.get_full_name() or self.request.user.username
            self.object.save()

            if formset.is_valid():
                formset.instance = self.object
                formset.save()

            else:
                return self.form_invalid(form)

        return super().form_valid(form)

class ReturnNoteDetailView(LoginRequiredMixin, DetailView):
    model = ReturnNote
    template_name = 'returns/return_detail.html'
    context_object_name = 'return_note'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        return context

@transaction.atomic
def create_from_dispatch(request, dispatch_id):
    dispatch_note = get_object_or_404(DispatchNote, pk=dispatch_id)
    if request.method == 'POST':
        return_note = ReturnNote.objects.create(
            dispatch_note=dispatch_note,
            client=dispatch_note.client,
            return_number=f'DEV-{dispatch_note.dispatch_number}',
            returned_by=request.user.get_full_name() or request.user.username
        )

        for item in dispatch_note.items.all():
            ReturnItem.objects.create(
                return_note=return_note,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price
            )

        messages.success(request, 'Nota de devolución creada con éxito.')
        return redirect('returns:detail', pk=return_note.pk)
    
    context = {
        'dispatch_note': dispatch_note,
    }
    return render(request, 'returns/create_from_dispatch_confirm.html', context)

@transaction.atomic
def process_return(request, pk):
    return_note = get_object_or_404(ReturnNote, pk=pk)
    if request.method == 'POST':
        for item in return_note.items.all():
            Movement.objects.create(
                product=item.product,
                movement_type='IN',
                quantity=item.quantity,
                unit_price=item.unit_price,
                delivered_to=return_note.returned_by,
                observations=f"Devolución procesada #{return_note.return_number}",
                created_by=request.user
            )

        return_note.status = 'PROCESSED'
        return_note.save()
        messages.success(request, 'Devolución procesada con éxito. El inventario ha sido actualizado.')
        return redirect('returns:detail', pk=return_note.pk)

    return redirect('returns:detail', pk=return_note.pk)