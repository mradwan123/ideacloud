from django.db import models
from django.utils import timezone

# Create your models here.

class ProjectGroup(models.Model):
    """
    This is a project group whuch was created under a project idea. It can be given a name and description
    """
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    #project_idea = models.ForeignKey(ProjectIdea, on_delete=models.CASCADE,  null=False, related_name='project_group-project_idea')
    #owner = models.ForeignKey(User, on_delete=models.CASCADE,  null=False, related_name='project_group-owner')
    members = models.ManyToManyField(User, blank=True, related_name='group-members')
    created_on = models.DateTimeField(null=False, editable=False, default=timezone.now)
    updated_on = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "project_idea"], name="unique_project_group_name"),
        ]

    def __str__(self):
        return f"{self.name} under {self.project_idea.title}"
