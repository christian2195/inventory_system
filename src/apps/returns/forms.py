# src/apps/returns/forms.py
from django import forms
from .models import ReturnNote, ReturnItem
from django.forms import inlineformset_factory

class ReturnNoteForm(forms.ModelForm):
    class Meta:
        model = ReturnNote
        fields = ['return_number', 'client', 'notes']
        widgets = {
            'return_number': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ReturnItemForm(forms.ModelForm):
    class Meta:
        model = ReturnItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

ReturnItemFormSet = inlineformset_factory(ReturnNote, ReturnItem, form=ReturnItemForm, extra=1, can_delete=True)