from rest_framework import serializers
from projects.models import ProjectIdea
from projects.serializers.serializer_profanity_validator import ProfanityValidator


class ProjectIdeaSerializer(serializers.ModelSerializer):
    # we define this here because it's a reverse relation (pointing back from ImageProject)
    # if we didn't do this, we wouldn't be able to return the images to the frontend, when they cacll for a ProjectIdea
    images_projects = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # this displays the author as a human-readable name rather than an ID; source can't be added via extra_kwargs
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = ProjectIdea
        fields = [
            'id',
            'title',
            'author',
            'description',
            'created_on',
            'tags',
            'likes',
            'images_projects'
        ]
        # The following code tells the serializer to not expect it in the POST data, and get the info from the view.
        # created_on is auto_now_add, so it must be read-only, IDs should never be changed
        read_only_fields = ['id', 'created_on']

        # this appends logic to the fields without overwriting default model behaviour
        extra_kwargs = {
            'title': {'validators': [ProfanityValidator()]},
            'description': {'validators': [ProfanityValidator()]},
        }

    def to_internal_value(self, data):
        """Sanitization; BEFORE validation. Turns incoming JSON into Python objects"""
        # we create a mutable copy of the data to allow modification because standard requests are immutable
        if hasattr(data, 'copy'):
            data = data.copy()

        if 'title' in data:
            data['title'] = data['title'].strip()
        if 'description' in data:
            data['description'] = data['description'].strip()
        # after our manual intervention, continue regularly
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """How it will look to the frontend; Python -> JSON"""
        # get the standard dictionary from the parent class
        representation = super().to_representation(instance)

        if instance.title:
            # alternatively we could use capitalize() here, depending on preference
            representation['title'] = instance.title.title()

        return representation
