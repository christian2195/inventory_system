# src/apps/movements/forms.py
from django import forms
from .models import Movement

class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ['product', 'quantity', 'movement_type', 'unit_price', 'delivered_to', 'observations']
        widgets = {
            'movement_type': forms.Select(choices=Movement.MOVEMENT_TYPES),
        }
        