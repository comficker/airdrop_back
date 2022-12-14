# Generated by Django 4.1.2 on 2022-11-07 14:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta', models.JSONField(blank=True, null=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('db_status', models.IntegerField(choices=[(-1, 'Deleted'), (0, 'Pending'), (1, 'Active')], default=1)),
                ('bio', models.CharField(blank=True, max_length=500, null=True)),
                ('options', models.JSONField(blank=True, null=True)),
                ('links', models.JSONField(blank=True, null=True)),
                ('refer_code', models.CharField(blank=True, max_length=50, null=True)),
                ('credits', models.FloatField(default=0)),
                ('achievements', models.JSONField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='links',
        ),
        migrations.RemoveField(
            model_name='wallet',
            name='options',
        ),
        migrations.AlterField(
            model_name='wallet',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wallet', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta', models.JSONField(blank=True, null=True)),
                ('updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('db_status', models.IntegerField(choices=[(-1, 'Deleted'), (0, 'Pending'), (1, 'Active')], default=1)),
                ('action_name', models.CharField(max_length=128)),
                ('value', models.FloatField()),
                ('message', models.JSONField(blank=True, null=True)),
                ('target_object_id', models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='authentication.profile')),
                ('target_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='target', to='contenttypes.contenttype')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
