from django.shortcuts import render, redirect, get_object_or_404

from main.decorators import admin_required

from .models import Config
from .forms import ConfigForm


@admin_required
def index(request, pk=None):

    configs = Config.objects.all()

    form_kwargs = {}

    if pk:
        form_kwargs['instance'] = get_object_or_404(Config, pk=pk)

    if request.method == 'POST':

        form = ConfigForm(request.POST, **form_kwargs)
        if form.is_valid():
            form.save()
            return redirect('config-index')
    else:

        form = ConfigForm(**form_kwargs)

    context = {
            'configs': configs,
            'form': form,
        }

    return render(request, 'config/index.html', context)


@admin_required
def delete(request, pk):
    config = get_object_or_404(Config, pk=pk)
    config.delete()
    return redirect('config-index')
