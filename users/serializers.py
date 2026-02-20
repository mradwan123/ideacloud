from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.validators import EmailValidator
from django.utils.html import strip_tags
from rest_framework.exceptions import ValidationError
from datetime import date

class PastDateValidator:
    """Ensuring date is not in the future"""
    
    # def __init__(self, field=None):
    #     self.field = field

    def __call__(self, value):
        
        if value > date.today():
            raise ValidationError('Error: Date should be in the past')


class UserSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(validators=[EmailValidator()])
    username = serializers.CharField(required=True, max_length=30, trim_whitespace=True)
    
    # Image validator:
    image = serializers.URLField(required=False, allow_null=True)
    
    description = serializers.TextField 
    available = serializers.BooleanField(default=False)
    created_on = serializers.DateTimeField(required=True, validators=[PastDateValidator()])
   
    #Other seriliazers
   
#    
    def to_internal_value(self, data):
        if 'username' in data:
            data['username'] = strip_tags(data['username'].strip())
        return super().to_internal_value(data)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Error: Duplicate email.')
        return value
    

    class Meta:
        model = User
        fields = ['id','username','email', 'available', 'image']
        
class UserRegisterSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(validators=[EmailValidator()])
    username = serializers.CharField(required=True, max_length=30, trim_whitespace=True)
    
    def to_internal_value(self, data):
        if 'username' in data:
            data['username'] = strip_tags(data['username'].strip())
        return super().to_internal_value(data)
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Error: Duplicate email.')
        return value
    
    class Meta :
        model = User 
        fields = ("id", "username","email","password")
        extra_kwargs = {'password': {'write_only': True}}

    #  override custom create so that we an check if user is None in view.py LoginView()
    def create (self, validated_data):
        user = User.objects.create_user(
            validated_data["username"],
            validated_data["email"],
            validated_data["password"]
        )
        return user