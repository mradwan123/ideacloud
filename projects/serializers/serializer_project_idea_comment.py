from rest_framework import serializers
from projects.models import ProjectIdeaComment

class ProjectIdeaCommentSerializer(serializers.ModelSerializer):
    class Meta:
      model = ProjectIdeaComment
      fields = ['id', 'user', 'content', 'project_idea']