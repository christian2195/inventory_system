from django import forms
from .models import Product, Movement, Supplier, MovementType

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'code', 'description', 'unit_of_measurement', 
            'current_stock', 'min_stock', 'unit_price', 'notes'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = [
            'date', 'product', 'movement_type', 
            'quantity', 'supplier', 'delivered_to', 
            'unit_price', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'code', 'contact', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class ReportForm(forms.Form):
    REPORT_CHOICES = [
        ('movements', 'Movimientos'),
        ('stock', 'Stock de Productos'),
    ]
    
    OUTPUT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]
    
    report_type = forms.ChoiceField(
        choices=REPORT_CHOICES, 
        label='Tipo de Reporte'
    )
    date_from = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Desde'
    )
    date_to = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Hasta'
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        label='Producto'
    )
    movement_type = forms.ModelChoiceField(
        queryset=MovementType.objects.all(),
        required=False,
        label='Tipo de Movimiento'
    )
    output_format = forms.ChoiceField(
        choices=OUTPUT_CHOICES,
        label='Formato de Salida'
    )

class ImportForm(forms.Form):
    FILE_TYPE_CHOICES = [
        ('products', 'Productos'),
        ('movements', 'Movimientos'),
    ]
    
    file = forms.FileField(label='Archivo Excel')
    file_type = forms.ChoiceField(
        choices=FILE_TYPE_CHOICES,
        label='Tipo de Datos a Importar'
    )