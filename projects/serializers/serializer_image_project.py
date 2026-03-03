from rest_framework import serializers
from ..models import ImageProject
from django.core.files.base import ContentFile
from PIL import Image
from config.image_helper.base64_image_conversion import base64_to_image
import uuid


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
            byte_data = base64_to_image(data["image"])

            filename = f"image_{uuid.uuid4().hex[:10]}.jpg"

            data["image"] = ContentFile(byte_data.getvalue(), filename)
        
        return super().to_internal_value(data)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if representation.get("project_idea"):
            del representation["project_idea"]

        return representation
    
    def validate_image(self, value):
        
        return value
