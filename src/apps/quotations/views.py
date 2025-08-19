from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Sum
from .models import Quotation, QuotationItem
from .forms import QuotationForm, QuotationItemFormSet
from inventory.models import Product

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
    success_url = reverse_lazy('quotations')
    
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
            
            # Calcular y guardar total
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