from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.authentication.models import User, Profile


@receiver(post_save, sender=User)
def on_user_post_save(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(
            user=instance
        )
