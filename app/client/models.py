from django.db import models


class Client(models.Model):

    name = models.CharField(max_length=250)
    api_key = models.CharField(max_length=50)
    api_secret = models.CharField(max_length=500)
    is_active = models.BooleanField(default=False, blank=True)
    redirect_uri = models.CharField(max_length=500)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
