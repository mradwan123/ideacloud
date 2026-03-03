from rest_framework import serializers
from projects.models import FinishedProject, Tag, ProjectGroup
from django.contrib.auth import get_user_model
from projects.serializers.serializer_profanity_validator import ProfanityValidator
from rest_framework.exceptions import ValidationError


User = get_user_model()


class FinishedProjectSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    # we're nesting the serializers here; the variable names HAVE to be the related_name of the model
    # read_only set to true because we wouldn't change anything from here

    # these are the annotated values from the queryset in the ProjectIdea views
    likes_count = serializers.IntegerField(read_only=True)
    has_liked = serializers.BooleanField(read_only=True)

    # This field handles both GET (display name) and POST (accept name), so we don't have to POST the IDs of the tags but can use the names
    # the tags HAVE to exist already in the DB!
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all())

    # "likes" been replaced with "likes_count" and "has_liked" to save bandwidth
    # DEPRECATED: likes = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = FinishedProject
        # not including "likes" anymore
        fields = [
            "id",
            "title",
            "description",
            "finished_on",
            "tags",
            "likes_count",
            "has_liked",
            "project_group"
        ]
        # The following code tells the serializer to not expect it in the POST data, and get the info from the view.
        # created_on is auto_now_add, so it must be read-only, IDs should never be changed
        read_only_fields = ["id", "finished_on"]

        # this appends logic to the fields without overwriting default model behaviour
        extra_kwargs = {
            "title": {"validators": [ProfanityValidator()]},
            "description": {"validators": [ProfanityValidator()]},
            # we must provide querysets for M2M fields so the serializer can find real objects
            "tags": {"queryset": Tag.objects.all()},
        }

    def to_internal_value(self, data):
        """Sanitization; BEFORE validation. Turns incoming JSON into Python objects"""
        # we create a mutable copy of the data to allow modification because standard requests are immutable
        if hasattr(data, "copy"):
            data = data.copy()

        if data.get("title"):
            data["title"] = data["title"].strip()
        if data.get("description"):
            data["description"] = data["description"].strip()
        # after our manual intervention, continue regularly
        return super().to_internal_value(data)

    def to_representation(self, instance):
        """How it will look to the frontend; Python -> JSON"""
        # get the standard dictionary from the parent class
        representation = super().to_representation(instance)

        if instance.title:
            # alternatively we could use capitalize() here, depending on preference
            representation["title"] = instance.title.title()

        return representation
    
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            project_group = validated_data['project_group']
            if project_group.owner == request.user:
                return super().create(validated_data)
        raise ValidationError("User is not allowed to publish this Finished Group. User is not owner of Project Group.")
            
            
    