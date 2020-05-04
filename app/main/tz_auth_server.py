from os import urandom
from urllib.parse import urlencode

from client.models import Client
from django.conf import settings

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

        base_uri = settings.SSO_GOV_MN['BASE_URI']
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

    def save_auth_code(self, user):

        token = Token()
        token.state_tz = self.state
        token.client = self.client


        token.client = self.client
        token.user = user
        token.generate_auth_code()
        # Stores redirect_uri for logging reasons
        token.redirect_uri = self.client.redirect_uri
        token.save()
        self.token = token
