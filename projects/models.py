from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Tag(models.Model):
    """These are the tags to categorize projects"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "tags"

    def __str__(self):
        return self.name

class ProjectIdea(models.Model):
    """This is the core Idea to a project. It is what eg. finished projects are based off"""

    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='author_project_ideas')
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='tags_project_ideas')
    likes = models.ManyToManyField(User, related_name='likes_project_ideas')

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
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='project_group_owner')
    members = models.ManyToManyField(User, blank=True, related_name='group_members')
    created_on = models.DateTimeField(null=False, editable=False, default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "project_idea"], name="unique_project_group_name"),
        ]

    def __str__(self):
        return f"Project Group: '{self.name}' Created under: '{self.project_idea.title}' Created on: {self.created_on}"

class ImageProject(models.Model):
    """The authenticated user uploads for images for new/active projects"""
    image = models.ImageField(upload_to='project_images/', null=False, blank=True)
    project_idea = models.ForeignKey(ProjectIdea, on_delete=models.CASCADE, related_name='images_projects')

    class Meta:
        db_table = "image_project"

    def __str__(self):
        return self.image
