from rest_framework import serializers
from projects.models import ProjectGroup, ProjectIdea
from projects.serializers.serializer_profanity_validator import ProfanityValidator
from rest_framework.serializers import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectGroupSerializer(serializers.ModelSerializer):
    """
    Serializer representing the model ProjectGroup in projects.
    It validates and sanatizes data in the communication between models and views.
    """

    class Meta:
        model = ProjectGroup
        fields = ['id',
                  'name',
                  'description',
                  'project_idea',
                  'owner',
                  'members',
                  'created_on',
                  'updated_on']

        read_only_fields = ['id',
                            'members',
                            'owner',
                            'project_idea',
                            'created_on',
                            'updated_on']

        # this appends logic to the fields without overwriting default model behaviour
        extra_kwargs = {
            'name': {'validators': [ProfanityValidator()]},
            'description': {'validators': [ProfanityValidator()]},
        }

    def to_internal_value(self, data):
        """Sanitization; BEFORE validation. Turns incoming JSON into Python objects"""
        if hasattr(data, 'copy'):
            data = data.copy()

        if 'name' in data:
            data['name'] = data['name'].strip()
        if 'description' in data:
            data['description'] = data['description'].strip()

        return super().to_internal_value(data)

    def to_representation(self, instance):
        """How it will look to the frontend; Python -> JSON"""
        representation = super().to_representation(instance)

        members_rep = []
        for member in instance.members.all():
            members_rep.append({"id": member.id,
                                "username": member.username})

        representation["members"] = members_rep

        representation["owner"] = {"id": instance.owner.id,
                                   "username": instance.owner.username}

        return representation

    def validate(self, data):
        """Check if the group is attached to a finished project and deny changes if so"""
        # instance exists during PUT/PATCH because its handling an existing database object, in POST it doens't
        if self.instance and self.instance.groups_finished_projects.exists():
            raise serializers.ValidationError("This group can't be modified because the project is already finished.")
        return data

    def validate_name(self, value):
        project_idea = self.context.get("project_idea")

        queryset = ProjectGroup.objects.filter(name=value, project_idea=project_idea)

        # if we are updating (instance exists), exclude ourselves from the search
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        # if anything is left in the queryset, it's a real duplicate, not our request instance
        if queryset.exists():
            raise ValidationError(f"Project group '{value}' under the project idea ’{project_idea.title}’.")

        return value

    def create(self, validated_data):
        request = self.context.get('request')

        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user

        project_idea = self.context.get("project_idea")

        if project_idea:
            validated_data['project_idea'] = project_idea

        # create group instance
        group = super().create(validated_data)

        # add the assigned owner to the group
        if group.owner:
            group.members.add(group.owner)

        return group
