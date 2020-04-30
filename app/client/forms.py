from django import forms

from .models import Client


class ClientForm(forms.ModelForm):

    class Meta:

        model = Client

        fields = [
            'name',
            'is_active',
            'redirect_uri',
        ]

        labels = {
            'name': 'Нэр',
            'is_active': 'Идэвхитэй эсэх',
            'redirect_uri': 'Redirect URI',
        }

        widgets = {}

        error_messages = {
            'name': {'required': 'оруулна уу!'},
            'redirect_uri': {'required': 'оруулна уу!'},
        }
