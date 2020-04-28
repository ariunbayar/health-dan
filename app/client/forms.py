from django import forms

from .models import Client


class ClientForm(forms.ModelForm):

    class Meta:

        model = Client

        fields = [
            'name',
            'is_active',
        ]

        labels = {
            'name': 'Нэр',
            'is_active': 'Идэвхитэй эсэх',
        }

        widgets = {}

        error_messages = {
            'name': {'required': 'оруулна уу!'},
        }
