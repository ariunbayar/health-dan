from django import forms

from .models import Config


class ConfigForm(forms.ModelForm):

    class Meta:

        model = Config

        fields = [
            'name',
            'value',
        ]

        labels = {
            'name': 'Нэр',
            'value': 'Утга',
        }

        widgets = {}

        error_messages = {
            'name': {'required': 'оруулна уу!'},
            'value': {'required': 'оруулна уу!'},
        }
