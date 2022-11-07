from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from apps.base.interface import BaseModel, HasIDString, BlockChain
from apps.media.models import Media
from apps.authentication.models import Profile
from utils.slug import unique_slugify


class Token(BaseModel, BlockChain):
    symbol = models.CharField(max_length=50)
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    type = models.CharField(default="ERC20", max_length=20)
    total_supply = models.FloatField(default=0)
    decimals = models.IntegerField(default=18)


# ================ FOR PROJECT
class Property(BaseModel, HasIDString):
    desc = models.CharField(max_length=600, blank=True, null=True)
    taxonomy = models.CharField(max_length=10, default="tag")
    media = models.ForeignKey(Media, related_name="terms", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = [['id_string', 'taxonomy']]


class Project(BaseModel, HasIDString):
    id_string = models.CharField(max_length=200, db_index=True)
    name = models.CharField(max_length=128, db_index=True)
    desc = models.CharField(max_length=600, blank=True, null=True)
    media = models.ForeignKey(Media, related_name="projects", on_delete=models.SET_NULL, null=True, blank=True)
    is_backer = models.BooleanField(default=False)

    links = models.JSONField(null=True, blank=True)
    properties = models.ManyToManyField(Property, related_name="projects", blank=True)

    # FOR HUNTER
    user = models.ForeignKey(
        User, related_name="hunted_projects", null=True, blank=True, db_index=True,
        on_delete=models.SET_NULL
    )


class Event(BaseModel, HasIDString):
    project = models.ForeignKey(
        Project,
        related_name="project_events",
        on_delete=models.CASCADE,
        db_index=True
    )
    name = models.CharField(max_length=128, null=True, blank=True)

    url = models.CharField(max_length=128, null=True, blank=True)
    title = models.CharField(max_length=128, null=True, blank=True)
    desc = models.CharField(max_length=600, blank=True, null=True)
    term = models.CharField(max_length=600, blank=True, null=True)

    credits = models.FloatField(default=0)
    prize_usd = models.FloatField(default=0)

    media = models.ForeignKey(Media, related_name="events", on_delete=models.SET_NULL, null=True, blank=True)
    tasks = models.JSONField(null=True, blank=True)
    properties = models.ManyToManyField(Property, related_name="events", blank=True)
    winners = models.JSONField(null=True, blank=True)

    is_exact_time = models.BooleanField(default=True)
    date_start = models.DateTimeField(default=timezone.now)
    date_end = models.DateTimeField(default=timezone.now)
    timeline = models.JSONField(null=True, blank=True)

    # FOR HUNTER
    user = models.ForeignKey(
        User, db_index=True,
        related_name="events",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    is_public = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    following = models.ManyToManyField(User, related_name="following_event", blank=True)
    joined = models.ManyToManyField(User, related_name="joined_event", blank=True)

    def save(self, **kwargs):
        if self.id is None and self.id_string is None or self.id_string == "":
            unique_slugify(self, self.title, "id_string")
        elif self.id is None and self.id_string:
            unique_slugify(self, self.id_string, "id_string")
        super(HasIDString, self).save(**kwargs)

    def approve(self):
        self.is_public = True
        if self.user:
            profile = self.user.profile
            if profile is None:
                Profile.objects.create(user=self.user)
            profile.make_achievements("create_event")

    def distribute_credits(self):
        pass


class Prize(BaseModel):
    event = models.ForeignKey(
        Event, db_index=True,
        related_name="prizes",
        on_delete=models.CASCADE
    )
    token = models.ForeignKey(Token, related_name="prizes", on_delete=models.CASCADE)
    value = models.FloatField(default=0)
    value_usd = models.FloatField(default=0)
    note = models.CharField(null=True, blank=True, max_length=500)


class Report(BaseModel):
    user = models.ForeignKey(
        User, db_index=True,
        related_name="reports",
        on_delete=models.CASCADE
    )
    event = models.ForeignKey(
        Event, db_index=True,
        related_name="reports",
        on_delete=models.CASCADE
    )
    content = models.CharField(max_length=1000)
    rate = models.IntegerField(default=1)


# ================ FOR INCENTIVE
class Incentive(BaseModel):
    event = models.ForeignKey(Event, related_name='incentives', on_delete=models.CASCADE)
    name = models.CharField(max_length=128, blank=True, null=True)
    desc = models.CharField(max_length=600, blank=True, null=True)
    token_id = models.ForeignKey(Token, related_name="incentives", on_delete=models.CASCADE)
    token_amount = models.FloatField(default=0)
    token_in_usd = models.FloatField(default=0)
    is_active = models.BooleanField(default=False)


class IncentiveDistribution(BaseModel):
    incentive = models.ForeignKey(Incentive, related_name="incentive_distributions", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="incentive_distributions", on_delete=models.CASCADE)
    earned = models.FloatField(default=0)
    is_claimed = models.BooleanField(default=False)
