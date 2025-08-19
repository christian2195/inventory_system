# src/apps/dispatch_notes/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import DispatchNote, DispatchItem

class DispatchNoteForm(forms.ModelForm):
    class Meta:
        model = DispatchNote
        fields = ['beneficiary', 'supplier', 'order_number', 'driver_name', 'driver_id', 'vehicle_type', 'vehicle_color', 'license_plate', 'observations']

class DispatchItemForm(forms.ModelForm):
    class Meta:
        model = DispatchItem
        fields = ['product', 'brand', 'model', 'quantity']

DispatchItemFormSet = inlineformset_factory(
    DispatchNote,
    DispatchItem,
    form=DispatchItemForm,
    extra=1,
    can_delete=True
)