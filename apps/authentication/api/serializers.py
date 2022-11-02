from rest_framework import serializers
from django.contrib.auth.models import User
from apps.authentication.models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id']

    def to_representation(self, instance):
        return super(WalletSerializer, self).to_representation(instance)


class UserSerializer(serializers.ModelSerializer):
    wallet = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'wallet']

    def get_wallet(self, instance):
        if hasattr(instance, 'wallet'):
            return WalletSerializer(instance.wallet).data
        else:
            wallet = Wallet(user=instance)
            wallet.save()
            return WalletSerializer(wallet).data
