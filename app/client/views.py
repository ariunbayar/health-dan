import os
import base64

from django.shortcuts import render, get_object_or_404, redirect

from main.decorators import admin_required

from .models import Client
from .forms import ClientForm


def _get_random_b64(length):
    return base64.b64encode(os.urandom(length)).decode('utf-8')


@admin_required
def index(request):

    clients = Client.objects.all()

    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.instance
            if not client.pk:
                client.api_key = _get_random_b64(16)
                client.api_secret = _get_random_b64(64)
            form.save()
            return redirect('client-index')
    else:
        form = ClientForm()

    context = {
        'clients': clients,
        'form': form,
    }

    return render(request, 'client/index.html', context)


@admin_required
def delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.tokens.all().delete()
    client.delete()
    return redirect('client-index')


@admin_required
def toggle_active(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.is_active = not client.is_active
    client.save()
    return redirect('client-index')
