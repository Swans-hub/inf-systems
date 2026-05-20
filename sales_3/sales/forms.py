from django import forms
from .models import FieldDefinition, DynamicRecord


class FieldDefinitionForm(forms.ModelForm):
    class Meta:
        model = FieldDefinition
        fields = ['name', 'label', 'field_type', 'order', 'is_active', 'precision']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'product_name'}),
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Наименование товара'}),
            'field_type': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'precision': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class DynamicRecordForm(forms.ModelForm):
    class Meta:
        model = DynamicRecord
        fields = []  # Убираем поле data из формы

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Динамически создаём поля на основе FieldDefinition
        fields_def = FieldDefinition.objects.filter(is_active=True)
        for field in fields_def:
            field_name = field.name
            field_label = field.label
            field_type = field.field_type

            if field_type == 'string':
                self.fields[field_name] = forms.CharField(
                    label=field_label,
                    required=True,
                    widget=forms.TextInput(attrs={'class': 'form-control'})
                )
            elif field_type == 'number':
                self.fields[field_name] = forms.FloatField(
                    label=field_label,
                    required=True,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
                )
            elif field_type == 'date':
                self.fields[field_name] = forms.DateField(
                    label=field_label,
                    required=True,
                    widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
                )

    def save(self, commit=True):
        # Собираем данные из динамических полей в JSON
        data = {}
        fields_def = FieldDefinition.objects.filter(is_active=True)
        for field in fields_def:
            value = self.cleaned_data.get(field.name)
            if value is not None:
                data[field.name] = value
        self.instance.data = data
        return super().save(commit)