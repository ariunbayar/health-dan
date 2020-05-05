from datetime import timedelta
from os import urandom
from base64 import b64encode

from django.db import models
from django.utils import timezone


# XXX what is the best name for this model?
class Token(models.Model):

    class Meta:
        ordering = ('-created_at',)

    client = models.ForeignKey('client.Client', on_delete=models.PROTECT, related_name='tokens')

    redirect_forward_uri = models.CharField(max_length=500)
    redirect_return_uri = models.CharField(max_length=500)

    auth_code_remote = models.CharField(max_length=256)

    # 96 bytes -> 128 chars (base64 encoded)
    auth_code = models.CharField(max_length=128, db_index=True)

    auth_code_expire_at = models.DateTimeField()

    access_token_remote = models.CharField(max_length=256, null=True)

    # 96 bytes -> 128 chars (base64 encoded)
    access_token = models.CharField(max_length=128, db_index=True, null=True)

    access_token_expire_at = models.DateTimeField(null=True)

    scope_remote = models.TextField(null=True)

    # JSON encoded service as scope
    scope = models.TextField(null=True)

    accessed_at = models.DateTimeField(null=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def generate_auth_code(self, expires_in=60):
        self.auth_code = b64encode(urandom(96)).decode()
        self.auth_code_expire_at = timezone.now() + timedelta(seconds=expires_in)

    def generate_access_token(self, expires_in=60):
        self.access_token = b64encode(urandom(96)).decode()
        self.access_token_expire_at = timezone.now() + timedelta(seconds=expires_in)
