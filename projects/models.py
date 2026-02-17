from django.db import models
from django.conf.settings import AUTH_USER_MODEL as User

class ProjectIdea(models.Model):
    """This is the core Idea to a project. It is what eg. finished projects are based off"""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='project_ideas')
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        author_name = self.author.username if self.author else "Deleted User"
        return f"Project: '{self.title}'\nSubmitted by: '{author_name}'\nCreated on: {self.created_on}"
