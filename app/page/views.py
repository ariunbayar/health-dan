from django.shortcuts import render
from oauth2.models import Token


def homepage(request):
    return render(request, 'page/homepage.html', {})


def instructions(request):
    return render(request, 'page/instructions.html', {})


def dashboard(request):
    max_tokens = 20
    tokens = Token.objects.all()[:max_tokens]
    context = {
            'tokens': tokens,
            'max_tokens': max_tokens,
        }
    return render(request, 'page/dashboard.html', context)
