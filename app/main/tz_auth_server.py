import base64
from os import urandom
import requests
from urllib.parse import urlencode

from django.conf import settings
from django.utils import timezone

from client.models import Client
from oauth2.models import Token


class TZAuthServerStep1():

    def __init__(self, request):
        self.request = request

    def is_forward_params_valid(self):

        api_key = self.request.GET.get('client_key')
        redirect_uri = self.request.GET.get('redirect_uri')
        state_client = self.request.GET.get('state')
        scope = self.request.GET.get('scope')

        client = Client.objects.filter(api_key=api_key).first()
        if not client:
            return False

        if not client.redirect_uri == redirect_uri:
            return False

        if not (state_client and scope):
            return False

        self.forward_params = {
                'api_key': api_key,
                'state_client': state_client,
                'scope': scope,
            }

        self.client = client

        return True

    def build_forward_uri(self):

        state = urandom(32).hex()

        self.request.session['forward_state_' + state] = {
                'api_key': self.forward_params['api_key'],
                'state_client': self.forward_params['state_client'],
                'redirect_forward_uri': settings.SSO_GOV_MN['CALLBACK_URI'],
            }

        base_uri = settings.SSO_GOV_MN['ENDPOINTS']['AUTHORIZE']
        if not base_uri.endswith('?'):
            base_uri += '?'

        params = {
                'response_type': 'code',
                'client_id': settings.SSO_GOV_MN['CLIENT_ID'],
                'redirect_uri': settings.SSO_GOV_MN['CALLBACK_URI'],
                'scope': self.forward_params['scope'],
                'state': state,
            }

        return base_uri + urlencode(params)

    def is_return_params_valid(self):

        auth_code = self.request.GET.get('code')
        state = self.request.GET.get('state')

        if not (state and auth_code):
            return False

        forward_state_options = self.request.session.get('forward_state_' + state, {})
        state_client = forward_state_options.get('state_client')
        api_key = forward_state_options.get('api_key')
        redirect_forward_uri = forward_state_options.get('redirect_forward_uri')

        if not (state_client and api_key and redirect_forward_uri):
            return False

        client = Client.objects.filter(api_key=api_key).first()
        if not client:
            return False

        self.return_params = {
                'client': client,
                'state_client': state_client,
                'auth_code': auth_code,
                'redirect_forward_uri': redirect_forward_uri,
            }

        return True

    def setup_auth_code(self):
        client = self.return_params['client']

        token = Token()
        token.client = client
        token.redirect_forward_uri = self.return_params['redirect_forward_uri']
        token.redirect_return_uri = client.redirect_uri
        token.auth_code_remote = self.return_params['auth_code']
        token.generate_auth_code()
        token.save()
        self.token = token

    def build_return_uri(self):
        params = {
            'auth_code': self.token.auth_code,
            'state': self.return_params['state_client'],
        }

        base_uri = self.token.client.redirect_uri
        if not base_uri.endswith('?'):
            base_uri += '?'

        return base_uri + urlencode(params)


class TZAuthServerStep2():

    BASE_HEADERS = {
            'User-Agent': 'tz.mohs.mn/api/ 1.0'
        }

    def __init__(self, request):
        self.request = request

    def is_forward_params_valid(self):

        auth_code = self.request.GET.get('auth_code')
        api_key = self.request.GET.get('client_key')
        api_secret = self.request.GET.get('client_secret')
        redirect_uri = self.request.GET.get('redirect_uri')

        if not self.request.method == 'POST':
            return False

        client = Client.objects.filter(api_key=api_key).first()
        if not client:
            return False

        if not client.redirect_uri == redirect_uri:
            return False

        if not client.api_secret == api_secret:
            return False

        token = Token.objects.filter(
                client=client,
                auth_code=auth_code,
                auth_code_expire_at__gt=timezone.now(),
                access_token__isnull=True,
            ).first()
        if not token:
            return False

        self.token = token

        return True

    def fetch_access_token(self):

        base_uri = settings.SSO_GOV_MN['ENDPOINTS']['TOKEN']
        if not base_uri.endswith('?'):
            base_uri += '?'

        params = {
                'grant_type': 'authorization_code',
                'code': self.token.auth_code_remote,
                'client_id': settings.SSO_GOV_MN['CLIENT_ID'],
                'client_secret': base64.b64encode(settings.SSO_GOV_MN['CLIENT_SECRET'].encode()),
                'redirect_uri': settings.SSO_GOV_MN['CALLBACK_URI'],
            }

        rsp = requests.post(base_uri + urlencode(params), headers=self.BASE_HEADERS)

        token_info = rsp.json()
        self.token.access_token_remote = token_info['access_token']
        self.token.scope_remote = token_info['scope']
        self.token.save()
        # TODO what to do with these?
        # token_info['token_type']
        # token_info['expires_in']

    def setup_access_token(self):
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
            'scope': self.token.scope_remote,
        }
        return rsp


class TZAuthServerStep3():

    BASE_HEADERS = {
            'User-Agent': 'tz.mohs.mn/api/ 1.0'
        }

    def __init__(self, request):
        self.request = request

    def is_request_valid(self):

        if not self.request.method == 'POST':
            return False

        try:
            auth_header = self.request.META.get('HTTP_AUTHORIZATION', ' ')
            token_type, access_token = auth_header.split(' ')
        except:
            token_type = None
            access_token = None

        if not access_token or not token_type == 'Bearer':
            return False

        token = Token.objects.filter(
                access_token_remote__isnull=False,
                access_token=access_token,
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

    def fetch_service_json(self):

        base_uri = settings.SSO_GOV_MN['ENDPOINTS']['SERVICE']

        headers = {
                **self.BASE_HEADERS,
                'Authorization': 'Bearer %s' % self.token.access_token_remote,
            }
        rsp = requests.post(base_uri, headers=headers)
        if rsp.status_code == 200:
            return rsp.text

        return '{"success": false}'
