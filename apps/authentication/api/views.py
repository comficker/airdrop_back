from rest_framework.response import Response
from django.contrib.auth.models import User
from apps.authentication.api.serializers import UserSerializer
from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import api_view
from rest_framework import status
from apps.media.models import Media


class UserViewSet(viewsets.ModelViewSet):
    models = User
    queryset = models.objects.order_by('-id')
    serializer_class = UserSerializer
    permission_classes = permissions.AllowAny,
    filter_backends = [OrderingFilter]
    search_fields = ['first_name', 'last_name', 'username']
    lookup_field = 'username'
    lookup_value_regex = '[\w.@+-]+'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        if instance.id != request.user.id:
            return Response({})
        # PRE
        if instance.profile.options is None:
            instance.profile.options = {}
        if request.data.get("options"):
            instance.profile.options = request.data.get("options")
            instance.profile.save()
        # Start
        if request.data.get("ws"):
            instance.profile.options["ws"] = request.data.get("ws")
        if request.data.get("nick"):
            instance.profile.nick = request.data.get("nick")
        if request.data.get("bio"):
            instance.profile.bio = request.data.get("bio")
        if request.data.get("extra"):
            instance.profile.extra = request.data.get("extra")
        if request.data.get("media"):
            media_instance = Media.objects.get(pk=int(request.data.get("media")))
            instance.profile.media = media_instance
        # END
        instance.profile.save()
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
            return Response(UserSerializer(user).data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
