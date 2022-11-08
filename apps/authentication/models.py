from django.db import models
from django.contrib.auth.models import User
from apps.base.interface import BaseModel
from apps.media.models import Media
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Profile(BaseModel):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    bio = models.CharField(max_length=500, null=True, blank=True)
    options = models.JSONField(blank=True, null=True)
    links = models.JSONField(blank=True, null=True)
    media = models.ForeignKey(Media, null=True, blank=True, related_name="profiles", on_delete=models.SET_NULL)

    inviter = models.ForeignKey('self', related_name="invitee", on_delete=models.SET_NULL, null=True, blank=True)
    refer_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    credits = models.FloatField(default=0)

    achievements = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    def make_achievements(self, flag, amount=1):
        if self.achievements is None:
            self.achievements = {
                "create_event": 0,
                "follow_event": 0,
                "join_event": 0,
                "create_referral_code": 0,
                "invite_friend": 0,
                "invite_view": 0
            }
        self.achievements[flag] = self.achievements.get(flag) + amount
        if not self.is_active \
                and self.achievements.get("create_event") >= 1 \
                and self.achievements.get("follow_event") >= 5 \
                and self.achievements.get("join_event") >= 5 \
                and self.achievements.get("create_referral_code") >= 1 \
                and self.achievements.get("invite_view") >= 5:
            self.is_active = True
        amount = 0
        if flag == "create_event":
            amount = 1
        if flag == "invite_friend":
            amount = 0.1
        if flag == "invite_view":
            amount = 0.001
        if amount > 0:
            self.make_transaction(flag, amount)
        self.save()

    def make_transaction(self, flag, amount, **kwargs):
        self.credits = self.credits + amount
        Transaction.objects.create(
            profile=self,
            action_name=flag,
            value=amount
        )
        self.save()


class Transaction(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profiles")
    action_name = models.CharField(max_length=128)
    value = models.FloatField()

    message = models.JSONField(null=True, blank=True)

    target_content_type = models.ForeignKey(
        ContentType, blank=True, null=True,
        related_name='target',
        on_delete=models.CASCADE, db_index=True
    )
    target_object_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )
    target = GenericForeignKey(
        'target_content_type',
        'target_object_id'
    )


class Wallet(BaseModel):
    chain_id = models.CharField(default="ethereum", max_length=100)
    address = models.CharField(max_length=100, db_index=True)
    user = models.OneToOneField(
        User,
        related_name='wallet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
