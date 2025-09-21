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