from django.contrib import admin
from apps.project.models import Media, Project, Token, Property, Event

# Register your models here.

admin.site.register((Media, Project, Token, Property, Event))
