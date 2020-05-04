from urllib.parse import urlencode
import logging

from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from client.models import Client
from main.tz_auth_server import TZAuthServerStep1

from .models import Token


def dan(request):

    tz_auth = TZAuthServerStep1(request)

    if not tz_auth.is_return_params_valid():
        raise Http404

    tz_auth.setup_auth_code()
    redirect_uri = tz_auth.build_return_uri()
    from django.http import HttpResponse; return HttpResponse('Redirect to: <br/>' + redirect_uri)  # TODO remove for production
    return redirect(redirect_uri)


def login(request):

    tz_auth = TZAuthServerStep1(request)

    if not tz_auth.is_forward_params_valid():
        raise Http404

    redirect_uri = tz_auth.build_forward_uri()
    from django.http import HttpResponse; return HttpResponse('Redirect to: <br/>' + redirect_uri)  # TODO remove for production
    return redirect(redirect_uri)


class AuthorizeEndpoint():

    def __init__(self, request):
        self.request_method = request.method
        self.auth_code = request.GET.get('auth_code')
        self.api_key = request.GET.get('client_key')
        self.api_secret = request.GET.get('client_secret')
        self.redirect_uri = request.GET.get('redirect_uri')

    def is_valid(self):

        if not self.request_method == 'POST':
            return False

        client = Client.objects.filter(api_key=self.api_key).first()
        if not client:
            return False

        if not client.redirect_uri == self.redirect_uri:
            return False

        if not client.api_secret == self.api_secret:
            return False

        token = Token.objects.filter(
                client=client,
                auth_code=self.auth_code,
                auth_code_expire_at__gt=timezone.now(),
                access_token__isnull=True,
            ).first()
        if not token:
            return False

        self.client = client
        self.token = token

        return True

    def set_access_token(self):
        expires_in = 61
        self.token.generate_access_token(expires_in)
        self.token.auth_code_expire_at = timezone.now()
        self.token.save()

    def build_rsp(self):
        expires_in = self.token.access_token_expire_at - timezone.now()
        rsp = {
            'access_token': self.token.access_token,
            'expires_in': expires_in.seconds,
            'token_type': 'Bearer',
            'scope': '',  # TODO
        }
        return rsp


@csrf_exempt
def authorize(request):

    # TODO implement

    authorize_endpoint = AuthorizeEndpoint(request)
    if not authorize_endpoint.is_valid():
        raise Http404

    authorize_endpoint.set_access_token()
    rsp = authorize_endpoint.build_rsp()

    return JsonResponse(rsp)


class ServiceEndpoint():

    def __init__(self, request):
        self.request_method = request.method

        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            self.token_type, self.access_token = auth_header.split(' ')
        except:
            self.token_type = None
            self.access_token = None

    def is_valid(self):

        if not self.request_method == 'POST':
            return False

        if not self.access_token or not self.token_type == 'Bearer':
            return False

        token = Token.objects.filter(
                access_token=self.access_token,
                access_token_expire_at__gt=timezone.now(),
                accessed_at__isnull=True,
            ).first()

        if not token:
            return False

        self.token = token

        return True

    def set_as_accessed(self):
        self.token.access_token_expire_at = timezone.now()
        self.token.accessed_at = timezone.now()
        self.token.save()

    def build_rsp(self):
        rsp = {
            'success': True,
            # TODO
        }
        return rsp


@csrf_exempt
def service(request):

    service_endpoint = ServiceEndpoint(request)
    if not service_endpoint.is_valid():
        raise Http404

    # TODO implement
    service_endpoint.set_as_accessed()
    rsp = service_endpoint.build_rsp()

    return JsonResponse(rsp)
