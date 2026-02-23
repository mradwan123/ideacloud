from rest_framework import serializers
from projects.models import ImageProject


class ImageProjectSerializer(serializers.ModelSerializer):
    class __init__(self):
        super().__init__()

    class Meta:
        model = ImageProject
        fields = ['id', 'image']
