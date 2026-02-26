from rest_framework import serializers
from projects.models import ProjectGroup
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
                            'created_on',
                            'updated_on']
        
        # this appends logic to the fields without overwriting default model behaviour
        extra_kwargs = {
            'title': {'validators': [ProfanityValidator()]},
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
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['owner'] = request.user
        return super().create(validated_data)
        