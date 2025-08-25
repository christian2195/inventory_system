# src/apps/dispatch_notes/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import DispatchNote, DispatchItem
from apps.inventory.models import Product  # Asegúrate de importar tu modelo de Producto

class DispatchNoteForm(forms.ModelForm):
    class Meta:
        model = DispatchNote
        fields = [
            'dispatch_number', 
            'client', 
            'beneficiary',
            'supplier',
            'order_number',
            'driver_name',
            'driver_id',
            'vehicle_type',
            'vehicle_color',
            'license_plate',
            'notes'
        ]
        widgets = {
            'dispatch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'beneficiary': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'order_number': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'driver_id': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_type': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle_color': forms.TextInput(attrs={'class': 'form-control'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DispatchItemForm(forms.ModelForm):
    # Campo oculto para guardar el ID del producto
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.HiddenInput(),
        required=False
    )
    # Campo visible para el autocompletado
    product_search = forms.CharField(
        label="Producto",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control product-autocomplete'})
    )

    class Meta:
        model = DispatchItem
        fields = ['product', 'quantity', 'unit_price', 'brand', 'model']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
        }

DispatchItemFormSet = inlineformset_factory(
    DispatchNote,
    DispatchItem,
    form=DispatchItemForm,
    extra=1,
    can_delete=True
)