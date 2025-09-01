# src/apps/dispatch_notes/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import DispatchNote, DispatchItem

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
    product_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control product-search',
            'placeholder': 'Buscar por código...'
        }),
        label="Código Producto"
    )
    
    product_description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'placeholder': 'Descripción del producto...'
        }),
        label="Descripción"
    )
    
    class Meta:
        model = DispatchItem
        fields = ['product', 'quantity', 'unit_price', 'brand', 'model']
        widgets = {
            'product': forms.HiddenInput(),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': '1',
                'placeholder': 'Cantidad'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar descripción del producto si existe
        if self.instance and self.instance.pk and self.instance.product_id:
            try:
                product = Product.objects.filter(pk=self.instance.product_id).first()
                if product:
                    self.fields['product_description'].initial = product.description
                    self.fields['product_search'].initial = product.product_code
            except Exception:
                pass
            
DispatchItemFormSet = inlineformset_factory(
    DispatchNote,
    DispatchItem,
    form=DispatchItemForm,
    extra=1,
    can_delete=True,
    max_num=500
)