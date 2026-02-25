from rest_framework import serializers
from projects.models import ImageProject


class ImageProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageProject
        fields = ['id', 'image', 'project_idea']
