# libros/forms.py
from django import forms
from .models import AsientoDiario

class AsientoDiarioForm(forms.ModelForm):
    class Meta:
        model = AsientoDiario
        fields = ['numero_asiento', 'fecha', 'descripcion', 'empresa']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos el campo de solo lectura
        self.fields['numero_asiento'].widget.attrs['readonly'] = True    