from apps.project import models
from apps.media.api.serializers import MediaSerializer
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
        self.fields["media"] = MediaSerializer(read_only=True)
        return super(ProjectListSerializer, self).to_representation(instance)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = '__all__'
        read_only_fields = ['db_status', 'created', 'updated', 'id_string']
        extra_fields = []

    def to_representation(self, instance):
        self.fields["media"] = MediaSerializer(read_only=True)
        return super(ProjectSerializer, self).to_representation(instance)


class EventListSerializer(serializers.ModelSerializer):
    total_task = serializers.SerializerMethodField()

    class Meta:
        model = models.Event
        fields = [
            "id_string",
            "title",
            "project",
            "date_start",
            "date_end",
            "total_task",
            "prizes"
        ]
        read_only_fields = ["prizes"]

    def to_representation(self, instance):
        self.fields["prizes"] = PrizeSerializer(read_only=True, many=True)
        self.fields["project"] = ProjectListSerializer(read_only=True)
        return super(EventListSerializer, self).to_representation(instance)

    def get_total_task(self, instance):
        return len(instance.tasks) if instance.tasks else 0


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Event
        fields = '__all__'
        read_only_fields = ['db_status', 'created', 'updated', 'user', 'is_public', 'following', 'joined', "media"]

    def to_representation(self, instance):
        self.fields["prizes"] = PrizeSerializer(read_only=True, many=True)
        self.fields["project"] = ProjectListSerializer(read_only=True)
        return super(EventSerializer, self).to_representation(instance)
