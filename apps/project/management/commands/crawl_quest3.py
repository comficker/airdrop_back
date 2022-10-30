import json
import pytz
import requests
from django.core.management.base import BaseCommand
from apps.project.models import Project, Token, Event, Prize
from apps.media.models import Media
from datetime import datetime


def fetch_quest3_details(id_str):
    re = requests.get(
        "https://api.quest3.xyz/consumer/quest/info/",
        params={
            "quest_id": id_str
        }
    )
    data = re.json()["result"]
    if type(data["basic"]["community_info"]["extra"]) is str:
        data["basic"]["community_info"]["extra"] = json.loads(data["basic"]["community_info"]["extra"])
    links = {
        **data["basic"]["community_info"]["extra"]
    }
    if data["basic"]["community_info"]["twitter_username"]:
        links["twitter"] = "https://twitter.com/{}".format(data["basic"]["community_info"]["twitter_username"])
    project, _ = Project.objects.get_or_create(
        id_string=data["basic"]["community_info"]["url"],
        defaults={
            "name": data["basic"]["community_info"]["name"],
            "desc": data["basic"]["community_info"]["introduction"][:500],
            "links": links
        }
    )
    if _:
        media = Media.objects.save_url(data["basic"]["community_info"]["logo"])
        if media:
            project.media = media
            project.save()
    tasks = list(map(lambda y: y["template_info"]["name"], data["task"]))
    event, _ = Event.objects.get_or_create(
        project=project,
        title=data["basic"]["title"],
        date_start=datetime.fromtimestamp(data["basic"]["start_time"], tz=pytz.utc),
        date_end=datetime.fromtimestamp(data["basic"]["end_time"], tz=pytz.utc),
        defaults={
            "tasks": tasks,
            "url": "https://app.quest3.xyz/quest/{}".format(id_str),
            "is_public": True
        }
    )
    if _:
        raw_rewards = []
        if data["rewards"]["rewards_info"]["nft_info"].get("contract_address"):
            raw_rewards.append(data["rewards"]["rewards_info"]["nft_info"])
        if data["rewards"]["rewards_info"]["token_info"].get("contract_address"):
            raw_rewards.append(data["rewards"]["rewards_info"]["token_info"])
        for raw in raw_rewards:
            token, x = Token.objects.get_or_create(
                symbol=raw["symbol"],
                address=raw["contract_address"],
                defaults={
                    "chain_id": raw["chain"]
                }
            )
            Prize.objects.get_or_create(
                event=event,
                token=token,
                defaults={
                    "value": raw.get("individual_benefits", 1)
                }
            )


def fetch_quest3(page):
    re = requests.get(
        "https://api.quest3.xyz/consumer/quest/list/",
        params={
            "count": 20,
            "page": page
        }
    )
    body = re.json()
    results = body["result"]["data"]
    for item in results:
        fetch_quest3_details(item["id"])
    if page < 19:
        fetch_quest3(page + 1)


class Command(BaseCommand):

    def handle(self, *args, **options):
        fetch_quest3(1)
        # fetch_quest3_details("699828831336562827")

# 400,
# 100501,
# 2201,
# 2600,
# 300,
# 10300,
# 200,
# 201,
# 202,
# 203,
# 100300,
# 204,
# 206,
# 205,
# 600,
# 10201,
# 100,
# 101,
# 102,
# 103,
# 100200,
# 2800,
# 501,
# 10101
# }
