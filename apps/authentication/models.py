from django.db import models
from django.contrib.auth.models import User
from apps.base.interface import BaseModel


class Wallet(BaseModel):
    chain_id = models.CharField(default="ethereum", max_length=100)
    address = models.CharField(max_length=100, db_index=True)
    user = models.OneToOneField(User, related_name='wallet', on_delete=models.CASCADE)
    bio = models.CharField(max_length=500, null=True, blank=True)
    options = models.JSONField(blank=True, null=True)
    links = models.JSONField(blank=True, null=True)
