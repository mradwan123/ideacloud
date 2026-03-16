from rest_framework import serializers
from projects.models import ProjectComment


class ProjectCommentSerializer(serializers.ModelSerializer):
    # this displays the author as a human-readable name rather than an ID; source can't be added via extra_kwargs
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = ProjectComment
        fields = [
            "id",
            "author",
            "content",
            "project_idea",
            "finished_project",
            "created_on",
            "updated_on"
        ]
        # these fields are injected directly in the views' save() methods, so they shouldn't be required in the incoming request data
        read_only_fields = ['project_idea', 'finished_project']
