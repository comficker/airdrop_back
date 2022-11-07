from django.core.management.base import BaseCommand
from apps.project.models import Project, Token
from apps.media.models import Media
import json


class Command(BaseCommand):

    def handle(self, *args, **options):
        for item in Project.objects.filter(id_string__startswith="bidshop-"):
            print(item.id_string)
            item.delete()