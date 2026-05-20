from django import forms
from django.core.exceptions import ValidationError
from .models import Counterparty

class CounterpartyForm(forms.ModelForm):
    class Meta:
        model = Counterparty
        fields = ['code', 'name', 'short_name', 'inn', 'kpp', 'ogrn',
                  'legal_address', 'actual_address', 'phone', 'email',
                  'is_active', 'comment']
        widgets = {
            'legal_address': forms.Textarea(attrs={'rows': 2}),
            'actual_address': forms.Textarea(attrs={'rows': 2}),
            'comment': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_inn(self):
        inn = self.cleaned_data.get('inn')
        if not inn:
            raise ValidationError('ИНН не может быть пустым!')
        inn = inn.strip()
        if len(inn) not in [10, 12] or not inn.isdigit():
            raise ValidationError('ИНН должен содержать 10 или 12 цифр')
        return inn