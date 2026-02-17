from django.db import models
from django.contrib.auth.models import User  # TODO remove this as soon as the custom user model works
from django.conf import settings

class ProjectIdea(models.Model):
    """This is the core Idea to a project. It is what eg. finished projects are based off"""
    title = models.CharField(max_length=200)
    # TODO replace 'User' with 'settings.AUTH_USER_MODEL'
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='project_ideas')
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        author_name = self.author.username if self.author else "Deleted User"
        return f"Project: '{self.title}'\nSubmitted by: '{author_name}'\nCreated on: {self.created_on}"
