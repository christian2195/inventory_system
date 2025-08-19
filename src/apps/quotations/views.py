# src/apps/quotations/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from .models import Quotation, QuotationItem
from .forms import QuotationForm, QuotationItemFormSet
from apps.inventory.models import Product
from apps.orders.models import Order, OrderItem

class QuotationListView(LoginRequiredMixin, ListView):
    model = Quotation
    template_name = 'quotations/quotation_list.html'
    context_object_name = 'quotations'
    paginate_by = 12
    
    def get_queryset(self):
        return super().get_queryset().prefetch_related('items').annotate(
            total=Sum('items__quantity')
        ).order_by('-date_created')

class QuotationDetailView(LoginRequiredMixin, DetailView):
    model = Quotation
    template_name = 'quotations/quotation_detail.html'
    context_object_name = 'quotation'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('product')
        context['total'] = sum(
            item.quantity * item.unit_price for item in context['items']
        )
        return context

class QuotationCreateView(LoginRequiredMixin, CreateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/quotation_form.html'
    success_url = reverse_lazy('quotations:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = QuotationItemFormSet(self.request.POST)
        else:
            context['formset'] = QuotationItemFormSet(queryset=QuotationItem.objects.none())
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object.save()
            
            total = 0
            instances = formset.save(commit=False)
            for instance in instances:
                instance.quotation = self.object
                instance.save()
                total += instance.quantity * instance.unit_price
            
            self.object.total = total
            self.object.save()
            
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class QuotationUpdateView(LoginRequiredMixin, UpdateView):
    model = Quotation
    form_class = QuotationForm
    template_name = 'quotations/quotation_form.html'
    success_url = reverse_lazy('quotations:list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = QuotationItemFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = QuotationItemFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        
        if formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                formset.save()
            return redirect(self.get_success_url())
        else:
            return self.render_to_response(self.get_context_data(form=form))

@transaction.atomic
def convert_to_order(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    
    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(
                client=quotation.client,
                order_number=f"ORD-{quotation.quotation_number}",
            )
            
            for item in quotation.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
            
            quotation.status = 'CONVERTED'
            quotation.save()
            
            return redirect('orders:detail', pk=order.pk)
            
    return render(request, 'quotations/convert_confirm.html', {'quotation': quotation})

@transaction.atomic
def approve_quotation(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    quotation.status = 'APPROVED'
    quotation.save()
    return redirect('quotations:detail', pk=pk)