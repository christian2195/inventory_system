# src/apps/returns/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import ReturnNote, ReturnItem

class ReturnNoteForm(forms.ModelForm):
    class Meta:
        model = ReturnNote
        fields = ['return_number', 'client', 'dispatch_note', 'notes']

class ReturnItemForm(forms.ModelForm):
    class Meta:
        model = ReturnItem
        fields = ['product', 'quantity', 'unit_price']

ReturnItemFormSet = inlineformset_factory(
    ReturnNote,
    ReturnItem,
    form=ReturnItemForm,
    extra=1,
    can_delete=True
)