from django.db import models


class Config(models.Model):

    class Meta:

        db_table = 'config'
        ordering = ('name',)

    name = models.CharField(max_length=250, db_index=True)
    value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
