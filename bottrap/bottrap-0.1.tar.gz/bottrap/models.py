from django.db import models


class BlockedIp(models.Model):
    ip = models.CharField(max_length=60)
    