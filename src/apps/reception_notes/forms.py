# src/apps/reception_notes/forms.py
from django import forms
from .models import ReceptionNote, ReceptionItem
from django.forms import inlineformset_factory

class ReceptionNoteForm(forms.ModelForm):
    class Meta:
        model = ReceptionNote
        fields = ['reception_number', 'supplier', 'notes']
        widgets = {
            'reception_number': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ReceptionItemForm(forms.ModelForm):
    class Meta:
        model = ReceptionItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

ReceptionItemFormSet = inlineformset_factory(ReceptionNote, ReceptionItem, form=ReceptionItemForm, extra=1, can_delete=True)