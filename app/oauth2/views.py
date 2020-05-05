from urllib.parse import urlencode
import logging

from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from client.models import Client
from main.tz_auth_server import TZAuthServerStep1
from main.tz_auth_server import TZAuthServerStep2
from main.tz_auth_server import TZAuthServerStep3

from .models import Token


def dan(request):

    tz_auth1 = TZAuthServerStep1(request)

    if not tz_auth1.is_return_params_valid():
        raise Http404

    tz_auth1.setup_auth_code()
    redirect_uri = tz_auth1.build_return_uri()
    from django.http import HttpResponse; return HttpResponse('Redirect to: <br/>' + redirect_uri)  # TODO remove for production
    return redirect(redirect_uri)


def login(request):

    tz_auth1 = TZAuthServerStep1(request)

    if not tz_auth1.is_forward_params_valid():
        raise Http404

    redirect_uri = tz_auth1.build_forward_uri()
    from django.http import HttpResponse; return HttpResponse('Redirect to: <br/>' + redirect_uri)  # TODO remove for production
    return redirect(redirect_uri)


@csrf_exempt
def authorize(request):

    tz_auth2 = TZAuthServerStep2(request)

    if not tz_auth2.is_forward_params_valid():
        raise Http404

    tz_auth2.fetch_access_token()
    tz_auth2.setup_access_token()
    rsp = tz_auth2.build_rsp()

    return JsonResponse(rsp)


@csrf_exempt
def service(request):

    tz_auth3 = TZAuthServerStep3(request)

    if not tz_auth3.is_request_valid():
        raise Http404

    tz_auth3.set_as_accessed()
    rsp = tz_auth3.fetch_service_json()

    return JsonResponse(rsp)
