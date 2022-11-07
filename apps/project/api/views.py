import base64
from django.utils import timezone
from django.db.models import Q, Case, When, IntegerField
from django.db.models import F
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import api_view
from apps.authentication.models import Profile, Transaction
from apps.base import pagination
from apps.project import models
from apps.media.models import Media
from utils.slug import vi_slug
from . import serializers

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


class TokenViewSet(viewsets.GenericViewSet, generics.ListCreateAPIView):
    models = models.Token
    queryset = models.objects.order_by('-created')
    serializer_class = serializers.TokenSerializer
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['symbol', 'title']
    lookup_field = 'pk'

    def create(self, request, *args, **kwargs):
        instance, _ = models.Token.objects.get_or_create(
            symbol=request.data.get("symbol")
        )
        return Response(serializers.TokenSerializer(instance).data)


class PropertyViewSet(viewsets.GenericViewSet, generics.ListCreateAPIView):
    models = models.Property
    queryset = models.objects.order_by('-created')
    serializer_class = serializers.PropertySerializer
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['name', 'desc']
    lookup_field = 'id_string'

    def list(self, request, *args, **kwargs):
        q = Q(db_status=1)
        if request.GET.get("taxonomy"):
            q = q & Q(taxonomy=request.GET.get("taxonomy"))
        if request.GET.get("id_string"):
            q = q & Q(id_string=request.GET.get("id_string"))
        queryset = self.filter_queryset(self.get_queryset().filter(q))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        taxonomy = request.data.get("taxonomy")
        instance, _ = models.Property.objects.get_or_create(
            name=name,
            taxonomy=taxonomy
        )
        return Response(serializers.PropertySerializer(instance).data)


class ProjectViewSet(viewsets.GenericViewSet, generics.ListCreateAPIView):
    models = models.Project
    queryset = models.objects.all()
    serializer_class = serializers.ProjectSerializer
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['name', 'desc']
    ordering_fields = [
        'name',
        'date_start',
        'date_end'
    ]
    lookup_field = 'id_string'

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = serializers.ProjectSerializer
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            context={
                'request': request
            })
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        id_string = vi_slug(request.data["name"])
        instance = models.Project.objects.filter(id_string=id_string).first()
        if instance:
            return Response(serializers.ProjectSerializer(instance).data, status=status.HTTP_201_CREATED)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class EventViewSet(viewsets.GenericViewSet, generics.ListCreateAPIView, generics.RetrieveAPIView):
    models = models.Event
    queryset = models.objects.all()
    serializer_class = serializers.EventListSerializer
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'id_string'

    def retrieve(self, request, *args, **kwargs):
        code = request.GET.get("referral_code")
        if code:
            # CHECK VISITOR AND MINT POINT TO PROFILE
            profile = Profile.objects.filter(refer_code=code).first()
            if profile:
                profile.make_achievements("invite_view")

        self.serializer_class = serializers.EventSerializer
        return super(EventViewSet, self).retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        order = ['relevance', 'time_diff']
        if request.GET.get("ordering"):
            order = request.GET.get("ordering").split(",")
        now = timezone.now()
        q = Q()
        if request.GET.get("is_mine") == "true" and request.user:
            q = q & Q(user=request.user)
        else:
            q = q & Q(is_public=True)
        if request.GET.get("is_following") == "true" and request.user:
            q = q & Q(following=request.user)
        if request.GET.get("is_joined") == "true" and request.user:
            q = q & Q(joined=request.user)
        if request.GET.get("project"):
            q = q & Q(project__id_string=request.GET.get("project"))
        if request.GET.get("page_name") == "upcoming":
            q = q & Q(date_start__gte=now)
        if request.GET.get("page_name") == "ongoing":
            q = q & Q(date_start__lte=now, date_end__gte=now, date_start__isnull=False)
        if request.GET.get("owner"):
            q = q & Q(user__id=request.GET.get("owner"))
        if request.GET.get("following"):
            q = q & Q(following__id=request.GET.get("following"))
        if request.GET.get("joining"):
            q = q & Q(joined__id=request.GET.get("joining"))

        qs = models.Event.objects.prefetch_related("project").filter(q)
        if "relevance" in order:
            qs = qs.annotate(
                relevance=Case(
                    When(date_start__gte=now, then=1),
                    When(date_start__lt=now, then=2),
                    output_field=IntegerField(),
                ))
        if "time_diff" in order:
            time_diff = F('date_end') - now
            if request.GET.get("page_name") == "upcoming":
                time_diff = now - F('date_start')
            if time_diff:
                qs = qs.annotate(
                    time_diff=time_diff
                    # time_diff=Case(
                    #     When(date_start__gte=now, then=F('date_start') - now),
                    #     When(date_start__lt=now, then=now - F('date_start')),
                    #     output_field=DurationField(),
                    # )
                )
        qs = qs.order_by(*order)
        queryset = self.filter_queryset(qs)
        page = self.paginate_queryset(queryset)
        if request.GET.get("project"):
            setattr(self.paginator, 'instance', serializers.ProjectSerializer(
                models.Project.objects.get(
                    id_string=request.GET.get("project")
                )
            ).data)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={
            'request': request,
        })
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        self.serializer_class = serializers.EventSerializer
        request.data["id_string"] = vi_slug(request.data["title"])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=request.user if request.user.is_authenticated else None
        )
        headers = self.get_success_headers(serializer.data)
        instance = models.Event.objects.get(pk=serializer.data["id"])
        if request.user.is_authenticated and request.user.username == "lam":
            instance.is_public = True
        if request.data.get("prizes"):
            for item in request.data["prizes"]:
                models.Prize.objects.create(
                    event_id=serializer.data["id"],
                    token_id=item.get("token"),
                    value=item.get("value"),
                    note=item.get("note")
                )
        if request.data.get("media"):
            raw_media = request.data.get("media")
            fm, img_str = raw_media.split(';base64,')
            ext = fm.split('/')[-1]
            file_name = instance.id_string + "." + ext
            data = ContentFile(base64.b64decode(img_str), name=file_name)
            media = Media(
                title=request.data.get("name"),
                path=data,
            )
            media.path.save(file_name, data)
            instance.media = media
        instance.meta = {
            "total_joined": 0,
            "total_following": 0
        }
        instance.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['GET', 'POST'])
def event_join(request, pk):
    instance = models.Event.objects.get(pk=pk)
    if request.user.is_authenticated:
        joined_list = instance.joined.all()
        if request.method == 'GET':
            return Response(request.user in joined_list, status=status.HTTP_200_OK)
        else:
            if instance.meta is None:
                instance.meta = {}
            if instance.meta.get("total_joined") is None:
                instance.meta["total_joined"] = 0
            if request.user in joined_list:
                instance.joined.remove(request.user)
            else:
                instance.joined.add(request.user)
            instance.meta["total_joined"] = instance.joined.count()
            instance.save()
            profile = request.user.profile
            if profile is None:
                profile = Profile.objects.create(user=request.user)
            profile.make_achievements("join_event")
            return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
def event_follow(request, pk):
    instance = models.Event.objects.get(pk=pk)
    if request.user.is_authenticated:
        follow_list = instance.following.all()
        if request.method == 'GET':
            return Response(request.user in follow_list, status=status.HTTP_200_OK)
        else:
            if instance.meta is None:
                instance.meta = {}
            if instance.meta.get("total_following") is None:
                instance.meta["total_following"] = 0
            if request.user in follow_list:
                instance.following.remove(request.user)
            else:
                instance.following.add(request.user)
            instance.meta["total_following"] = instance.following.count()
            instance.save()
            profile = request.user.profile
            if profile is None:
                profile = Profile.objects.create(user=request.user)
            profile.make_achievements("follow_event")
            return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
