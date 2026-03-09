from django.contrib import admin
from .models import ProjectIdea, ProjectGroup, Tag, FinishedProject, ImageProject

admin.site.register(ProjectIdea)
admin.site.register(ProjectGroup)
admin.site.register(Tag)
admin.site.register(FinishedProject)
admin.site.register(ImageProject)
