from urllib.parse import urlencode
import logging

from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from client.models import Client
from .models import Token


def dan(request):
    # TODO implement
    pass


class LoginEndpoint():

    def __init__(self, request):
        self.api_key = request.GET.get('client_key')
        self.redirect_uri = request.GET.get('redirect_uri')
        self.state = request.GET.get('state')

    def is_valid(self):

        client = Client.objects.filter(api_key=self.api_key).first()
        if not client:
            return False

        if not client.redirect_uri == self.redirect_uri:
            return False

        self.client = client

        return True

    def save_auth_code(self, user):
        token = Token()
        token.client_state = self.state
        token.client = self.client
        token.user = user
        token.generate_auth_code()
        # Stores redirect_uri for logging reasons
        token.redirect_uri = self.client.redirect_uri
        token.save()
        self.token = token

    def build_redirect_uri(self):

        params = {
            'auth_code': self.token.auth_code,
            'state': self.token.client_state,
        }

        base_uri = self.token.client.redirect_uri
        if not base_uri.endswith('?'):
            base_uri += '?'

        return base_uri + urlencode(params)


def login(request):

    # TODO implement sso.gov.mn

    # if request.GET.get('autologin') == 'yes':
    if request.method == 'POST':

        login_endpoint = LoginEndpoint(request)

        if not login_endpoint.is_valid():
            raise Http404

        # TODO this block is to be rewritten
        from user.models import User
        from django.contrib import auth
        user = User.objects.filter(is_superuser=True).first()
        auth.login(request, user)

        login_endpoint.save_auth_code(user)
        uri = login_endpoint.build_redirect_uri()

        return redirect(uri)

    return render(request, 'secure/login.html', {})


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
