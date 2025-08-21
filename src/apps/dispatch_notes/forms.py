# src/apps/dispatch_notes/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import DispatchNote, DispatchItem

class DispatchNoteForm(forms.ModelForm):
    class Meta:
        model = DispatchNote
        fields = ['dispatch_number', 'client', 'notes']
        widgets = {
            'dispatch_number': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DispatchItemForm(forms.ModelForm):
    class Meta:
        model = DispatchItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

DispatchItemFormSet = inlineformset_factory(
    DispatchNote,
    DispatchItem,
    form=DispatchItemForm,
    extra=1,
    can_delete=True
)