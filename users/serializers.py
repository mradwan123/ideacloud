from django.contrib.auth import get_user_model
from projects.models import ProjectIdea
from rest_framework import serializers
from django.core.validators import EmailValidator
from django.utils.html import strip_tags
from rest_framework.exceptions import ValidationError
from datetime import date
from projects.serializers.serializer_profanity_validator import ProfanityValidator
from django.contrib.auth.password_validation import validate_password as django_validate_password
from config.image_helper.base64_image_conversion import base64_to_image
from django.core.files.base import ContentFile
from config.settings import DEFAULT_PROFILE_IMAGE_URL
from config.image_helper.validate_image import is_image_valid
import os


User = get_user_model()

class PastDateValidator:
    """Ensuring date is not in the future"""

    # def __init__(self, field=None):
    #     self.field = field

    def __call__(self, value):

        if value > date.today():
            raise ValidationError('Error: Date should be in the past')

class ProjectUsersRepresentationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectIdea
        fields = ['id', 'title']

class UserSerializer(serializers.ModelSerializer):

    # From Abstract
    username = serializers.CharField(required=True, max_length=100)
    password = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True, validators=[EmailValidator()])
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=30)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=100)

    # Image validator: see to_internal_value below
    image = serializers.ImageField(required=False, allow_null=True)

    description = serializers.CharField(default="", allow_blank=True, max_length=1000, trim_whitespace=True)
    available = serializers.BooleanField(default=False)

    # many-to-many relations
    favorite_projects = ProjectUsersRepresentationSerializer(many=True, read_only=True)
    interested_projects = ProjectUsersRepresentationSerializer(many=True, read_only=True)

    def to_internal_value(self, data):
        # Make a mutable copy
        if hasattr(data, 'copy'):
            data = data.copy()

        if 'username' in data:
            data['username'] = strip_tags(data['username']).strip()
        if 'first_name' in data:
            data['first_name'] = strip_tags(data['first_name']).strip()
        if 'last_name' in data:
            data['last_name'] = strip_tags(data['last_name']).strip()
        if 'description' in data:
            data['description'] = strip_tags(data['description']).strip()
            
        
        # Handle base64 image if present. Check to see if image is URL. 
        if data.get("image"):
            try:
                data["image"] = base64_to_image(data["image"])
            except ValueError:
                raise ValidationError({"error": "Invalid image format. Image has to be jpg."})

        return super().to_internal_value(data)
    
    def validate_username(self, value):
        """
        Validate username uniqueness:
        - For new users (POST): Check if username exists at all
        - For updates (PUT/PATCH): Check if username exists for a DIFFERENT user
        """
        # Check if any user has this username
        existing_user = User.objects.filter(username=value).first()
        
        # If this is a new user (no instance)
        if not self.instance:
            if existing_user:
                raise serializers.ValidationError('Error: Duplicate username.')
        
        # If this is an update (has instance)
        else:
            # If username exists AND it belongs to a DIFFERENT user
            if existing_user and existing_user.id != self.instance.id:
                raise serializers.ValidationError('Error: This username is already taken by another user.')
        
        # Always return the value
        return value
                

    def validate_password(self, value):
        """Changed name of built in and checking here"""
        try:
            django_validate_password(value)
        except ValidationError as error:
            raise serializers.ValidationError(error.message)
        return value

    # def to_representation(self, instance):
    #     '''This will be used by Front End to represent the project by ID'''
    #     representation = super().to_representation(instance)

    #     representation['favorite_projects'] = instance.favorite_projects.project_idea.title()
    #     representation['interested_projects'] = instance.interested_projects.project_idea.title()
    #     return representation

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'available',
                  'image', 'description', 'created_on', 'favorite_projects', 'interested_projects']
        read_only_fields = ['id', 'created_on']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

        # this appends logic to the fields without overwriting default model behaviour
    extra_kwargs = {
        'password': {'write_only': True},
        'title': {'validators': [ProfanityValidator()]},
        'description': {'validators': [ProfanityValidator()]}
    }
    
    def validate_image(self, value):
        if value and not is_image_valid(value):
            raise ValidationError("Image could not be saved. Has to be jpg in base64 format.")
        
        return value
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if not representation.get("image"):
            representation["image"] = DEFAULT_PROFILE_IMAGE_URL

        return representation
    
    def update(self, instance, validated_data):
        if "image" in validated_data.keys():
            if instance.image and not instance.image.path.endswith("default.jpg") and os.path.isfile(instance.image.path):
                os.remove(instance.image.path)

        return super().update(instance, validated_data)
    
    

