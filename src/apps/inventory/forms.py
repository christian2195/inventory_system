from django import forms
from .models import Product  # Importación relativa del modelo

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'  # o lista campos específicos