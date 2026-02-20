from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    '''
    Docstring for User class:
    Custom User model extending and adding to the AbstractUser by Django.
    Standard User fields plus(image, description, created_on, finsihed_projects)
    '''
   
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.jpg')
    description = models.TextField(max_length=1000, null=True, blank=True)
    available = models.BooleanField(default=False)
    # Automatically sets the field to the current date only when the model instance is first created.
    created_on = models.DateTimeField(auto_now_add=True, editable=False)  
    favorite_projects = models.ManyToManyField("projects.ProjectIdea", related_name='user_favorite_project_idea', blank=True)
    interested_projects = models.ManyToManyField("projects.ProjectIdea", related_name='user_interested_project_idea', blank=True)    
    
    
    def __str__(self):
        return self.username
