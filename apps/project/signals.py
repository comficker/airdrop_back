from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.project.models import Event
from apps.authentication.models import Profile

