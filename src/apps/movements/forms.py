from django import forms
from .models import Movement, DispatchItem  # Importa desde el mismo app
from .models import DispatchNote

class MovementForm(forms.ModelForm):
    class Meta:
        model = Movement
        fields = ['entry', 'movement_number', 'movement_type']
        widgets = {
            'movement_type': forms.Select(choices=Movement.MOVEMENT_TYPES),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# Primero define el FormSet usando inlineformset_factory
DispatchItemFormSet = inlineformset_factory(
    DispatchNote,
    DispatchItem,
    form=DispatchItemForm,
    extra=1,
    can_delete=True
)
class DispatchItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if form.is_valid() and not form.cleaned_data.get('DELETE', False):
                # Validación personalizada aquí
                pass
    class Meta:
        model = DispatchItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }
class DispatchNoteForm(forms.ModelForm):
    class Meta:
        model = DispatchNote
        fields = ['date', 'reference', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }