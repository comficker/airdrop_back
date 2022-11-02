from apps.project import models
from apps.media.api.serializers import SimpleMediaSerializer
from rest_framework import serializers


class TokenListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Token
        fields = ["symbol"]


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Token
        fields = '__all__'
        read_only_fields = ['db_status', 'created', 'updated', ]
        extra_fields = []


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Property
        fields = '__all__'
        read_only_fields = ['db_status', 'created', 'updated', ]
        extra_fields = []


class PrizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Prize
        fields = ["token", "value"]

    def to_representation(self, instance):
        self.fields["token"] = TokenListSerializer(read_only=True)
        return super(PrizeSerializer, self).to_representation(instance)


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ["id_string", "name", "media"]

    def to_representation(self, instance):
        self.fields["media"] = SimpleMediaSerializer(read_only=True)
        return super(ProjectListSerializer, self).to_representation(instance)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = '__all__'
        read_only_fields = ['db_status', 'created', 'updated', 'id_string']
        extra_fields = []

    def to_representation(self, instance):
        self.fields["media"] = SimpleMediaSerializer(read_only=True)
        return super(ProjectSerializer, self).to_representation(instance)


class EventListSerializer(serializers.ModelSerializer):
    is_joined = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    total_tasks = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = [
            "id_string",
            "url",
            "title",
            "project",
            "date_start",
            "date_end",
            "prizes",
            "meta",
            "is_joined",
            "is_following",
            "total_tasks"
        ]
        read_only_fields = ["prizes"]

    def to_representation(self, instance):
        self.fields["prizes"] = PrizeSerializer(read_only=True, many=True)
        self.fields["project"] = ProjectListSerializer(read_only=True)
        return super(EventListSerializer, self).to_representation(instance)

    def get_is_joined(self, instance):
        if self.context.get("request") and self.context["request"].user.is_authenticated:
            return self.context["request"].user in instance.joined.all()
        return False

    def get_is_following(self, instance):
        if self.context.get("request") and self.context["request"].user.is_authenticated:
            return self.context["request"].user in instance.following.all()
        return False

    def get_total_tasks(self, instance):
        return len(instance.tasks) if instance.tasks else 0


class EventSerializer(serializers.ModelSerializer):
    is_joined = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = [
            "name",
            "id", "id_string", "is_joined", "is_following", "meta", "desc", "meta", "tasks", "project", "prizes",
            "date_start", "date_end"
        ]
        read_only_fields = [
            'db_status', 'created', 'updated', 'user', 'is_public', 'following', 'joined', "media", "meta",
            "is_joined",
            "is_following"
        ]

    def to_representation(self, instance):
        self.fields["prizes"] = PrizeSerializer(read_only=True, many=True)
        self.fields["project"] = ProjectListSerializer(read_only=True)
        return super(EventSerializer, self).to_representation(instance)

    def get_is_joined(self, instance):
        if self.context.get("request") and self.context["request"].user.is_authenticated:
            return self.context["request"].user in instance.joined.all()
        return False

    def get_is_following(self, instance):
        if self.context.get("request") and self.context["request"].user.is_authenticated:
            return self.context["request"].user in instance.following.all()
        return False
