from django.db import models
# from users.models import User
from django.contrib.auth.models import User  # TODO remove this later and replace with line above
from django.utils import timezone


class ProjectIdea(models.Model):
    """This is the core Idea to a project. It is what eg. finished projects are based off"""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='project_ideas')
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        author_name = self.author.username if self.author else "Deleted User"
        return f"Project: '{self.title}' Submitted by: '{author_name}' Created on: {self.created_on}"


class ProjectGroup(models.Model):
    """
    This is a project group whuch was created under a project idea. It can be given a name and description
    """
    name = models.CharField(max_length=200, null=False)
    description = models.TextField()
    project_idea = models.ForeignKey(ProjectIdea, on_delete=models.CASCADE, null=False, related_name='project_group_project_idea')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='project_group_owner')
    members = models.ManyToManyField(User, blank=True, related_name='group_members')
    created_on = models.DateTimeField(null=False, editable=False, default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "project_idea"], name="unique_project_group_name"),
        ]

    def __str__(self):
        return f"Project Group: '{self.name}' Created under: '{self.project_idea.title}' Created on: {self.created_on}"
