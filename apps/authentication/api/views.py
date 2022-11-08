import base64
from rest_framework.response import Response
from django.contrib.auth.models import User
from apps.authentication.api.serializers import UserSerializer, TransactionSerializer, ProfileSerializer, \
    ProfileListSerializer
from rest_framework import generics, viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.decorators import api_view
from rest_framework import status
from apps.media.models import Media
from apps.authentication.models import Profile, Transaction
from apps.base import pagination
from django.core.files.base import ContentFile


class UserViewSet(viewsets.ModelViewSet):
    models = User
    queryset = models.objects.order_by('-id')
    serializer_class = UserSerializer
    permission_classes = permissions.AllowAny,
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['first_name', 'last_name', 'username']
    lookup_field = 'username'
    lookup_value_regex = '[\w.@+-]+'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        if instance.id != request.user.id:
            return Response({})
        # PRE
        profile = instance.profile
        if profile is None:
            profile = Profile.objects.create(user=instance)
        if profile.options is None:
            profile.options = {}
        if profile.links is None:
            profile.links = {}
        # Start
        if request.data.get("bio"):
            profile.bio = request.data.get("bio")
        if request.data.get("links"):
            profile.links = request.data.get("links")
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
            profile.media = media
        # END
        profile.save()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_204_NO_CONTENT)


class TransactionViewSet(viewsets.GenericViewSet, generics.ListAPIView):
    models = Transaction
    queryset = models.objects.order_by("-created")
    serializer_class = TransactionSerializer
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['profile', 'action_name']
    ordering_fields = ['created']
    lookup_field = 'pk'


class ProfileViewSet(viewsets.GenericViewSet, generics.RetrieveAPIView, generics.ListAPIView):
    models = Profile
    queryset = models.objects.all()
    serializer_class = ProfileListSerializer
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['bio']
    ordering_fields = ['credits']
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        self.serializer_class = ProfileSerializer
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        if kwargs["pk"] == "0" and request.user.is_authenticated and request.user.profile is None:
            instance = Profile.objects.create(user=request.user)
        else:
            instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def get_auth_user(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == "POST":
        err = []
        if not request.data.get("email"):
            err.append("REGISTER_EMAIL_BLANK")
        else:
            if User.objects.filter(email=request.data.get("email")).first():
                err.append("REGISTER_EMAIL_DUPLICATED")
        if not request.data.get("username"):
            err.append("REGISTER_USERNAME_BLANK")
        else:
            if User.objects.filter(username=request.data.get("username")).first():
                err.append("REGISTER_USERNAME_DUPLICATED")
        if not request.data.get("password_1") or not request.data.get("password_2"):
            err.append("REGISTER_PASSWORD_BLANK")
        if request.data.get("password_1") != request.data.get("password_2"):
            err.append("REGISTER_PASSWORD_MISSMATCH")
        if len(err):
            return Response(err, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.create_user(
                username=request.data["username"],
                email=request.data["email"],
                password=request.data["password_1"]
            )
            code = request.data.get("referral_code")
            if code:
                inviter = Profile.objects.filter(refer_code=code).first()
                if inviter:
                    user.profile.inviter = inviter
                    user.profile.save()
                    user.profile.make_achievements("invite_friend")
            return Response(UserSerializer(user).data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_referral_code(request):
    code = request.data.get("referral_code")
    if Profile.objects.filter(refer_code=code).first() is None:
        current_profile = request.user.profile
        if current_profile is None:
            current_profile = Profile.objects.create(user=request.user)
        current_profile.refer_code = code
        current_profile.save()
        current_profile.make_achievements("create_referral_code")
