from django.shortcuts import render, redirect
from django.contrib import auth

from user.models import User


def login(request):
    if request.method == 'POST':
        if request.POST.get('autologin') == 'yes':
            user = User.objects.filter(is_superuser=True).first()
            auth.login(request, user)
            return redirect('page-homepage')

    return render(request, 'secure/login.html', {})


def logout(request):
    auth.logout(request)
    return redirect('page-homepage')
