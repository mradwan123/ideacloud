from django.contrib import admin
from .models import ProjectIdea, ProjectGroup, Tag

admin.site.register(ProjectIdea)
admin.site.register(ProjectGroup)
admin.site.register(Tag)
