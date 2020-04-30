from functools import wraps

from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect


def admin_required(f):
    @wraps(f)
    def inner(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)

        if not request.user.is_superuser:
            raise Http404

        return f(request, *args, **kwargs)

    return inner
