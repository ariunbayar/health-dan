from django.shortcuts import render


def homepage(request):
    return render(request, 'page/homepage.html', {})


def instructions(request):
    return render(request, 'page/instructions.html', {})
