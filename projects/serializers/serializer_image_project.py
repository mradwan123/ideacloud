from rest_framework import serializers
from ..models import ImageProject
from django.core.files.base import ContentFile
from PIL import Image
from config.image_helper.base64_image_conversion import base64_to_image
from config.image_helper.validate_image import is_image_valid
import uuid
from rest_framework.exceptions import ValidationError


class ImageProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = ImageProject
        fields = ['id', 'image', 'project_idea']
        extra_kwargs = {
            "image": {"required": True},
        }

    def to_internal_value(self, data):
        """Sanitization; BEFORE validation. Turns incoming JSON into Python objects"""
        # we create a mutable copy of the data to allow modification because standard requests are immutable
        if hasattr(data, 'copy'):
            data = data.copy()

        if data.get("image"):          
            try:
                data["image"] = base64_to_image(data["image"])
            except ValueError:
                raise ValidationError({"error": "Invalid image format. Image has to be jpg."})

        return super().to_internal_value(data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation.get("project_idea"):
            del representation["project_idea"]

        return representation

    def validate_image(self, value):

        if not is_image_valid(value):
            raise ValidationError("Image could not be saved. Has to be jpg in base64 format.")

        return value
    
