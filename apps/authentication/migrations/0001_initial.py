# Generated by Django 4.1.2 on 2022-11-02 16:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta', models.JSONField(blank=True, null=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('db_status', models.IntegerField(choices=[(-1, 'Deleted'), (0, 'Pending'), (1, 'Active')], default=1)),
                ('chain_id', models.CharField(default='ethereum', max_length=100)),
                ('address', models.CharField(db_index=True, max_length=100)),
                ('bio', models.CharField(blank=True, max_length=500, null=True)),
                ('options', models.JSONField(blank=True, null=True)),
                ('links', models.JSONField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='wallet', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]