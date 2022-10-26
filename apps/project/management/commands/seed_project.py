from django.core.management.base import BaseCommand
from apps.project.models import Project, Token
from apps.media.models import Media
import json


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('seed.json') as json_file:
            dataset = json.load(json_file)
            for item in dataset["token"]:
                Token.objects.get_or_create(
                    symbol=item["symbol"],
                    defaults={
                        "type": item["type"],
                        "chain_id": item["chain_id"],
                        "address": item["address"]
                    }
                )
            for item in dataset["project"]:
                media = Media.objects.save_url(item["media"])
                Project.objects.get_or_create(
                    name=item["name"],
                    defaults={
                        "desc": item["desc"],
                        "media": media,
                        "links": item["links"],
                    }
                )
