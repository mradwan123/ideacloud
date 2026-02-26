from rest_framework import serializers
from projects.models import ImageProject
from config.image_helper.base64_image_conversion import base64_to_image
from django.core.files.base import ContentFile

class ImageProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageProject
        fields = ['id', 'image', 'project_idea']

    def to_internal_value(self, data):
        """Sanitization; BEFORE validation. Turns incoming JSON into Python objects"""
        # we create a mutable copy of the data to allow modification because standard requests are immutable
        if hasattr(data, 'copy'):
            data = data.copy()

        if data.get("image"):

            data["image"] = base64_to_image(data["image"])
        
        return super().to_internal_value(data)
