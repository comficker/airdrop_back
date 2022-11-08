from rest_framework import serializers
from django.contrib.auth.models import User
from apps.authentication.models import Wallet, Profile, Transaction


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id']

    def to_representation(self, instance):
        return super(WalletSerializer, self).to_representation(instance)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'profile']


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'media']

    def to_representation(self, instance):
        self.fields["user"] = UserSerializer(read_only=True)
        return super(ProfileListSerializer, self).to_representation(instance)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'bio', 'options', 'links',
            'media', 'refer_code', 'credits',
            'achievements', 'is_active'
        ]

    def to_representation(self, instance):
        self.fields["user"] = UserSerializer(read_only=True)
        return super(ProfileSerializer, self).to_representation(instance)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'profile', 'action_name', 'value', 'message'
        ]
