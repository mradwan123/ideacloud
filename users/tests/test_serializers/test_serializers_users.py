from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.urls import reverse
from ...serializers import UserSerializer 


#------ Testing UserSerializer & UserRegisterSerializer

class UserSerializerTest(TestCase):
    """Description"""

    def setUp(self):
        # Create users
        self.user_data = {
                    'first_name': 'firstname',
                    'last_name': 'lastname',
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'Tests123',
                    'description': 'test description',  
                }

    def test_new_user_seriliazer(self):
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], self.user_data['username'])
        self.assertEqual(serializer.validated_data['email'], self.user_data['email'])
        self.assertEqual(serializer.validated_data['description'], self.user_data['description'])
                     

     #TODO - complete tests    

        
        
    # def test_user_serializer_output_fields(self):
    #     """Test that the simple UserSerializer only shows id, username, and email"""
        
    #     serializer = UserSerializer(data=self.user_data)

    #     expected_fields = ['id','username','email', 'first_name', 'last_name', 'available', 
    #               'image', 'description', 'created_on', 'favorite_projects', 'interested_projects']
   
    #     self.assertEqual(set(serializer.data.keys()), expected_fields)
    #     # Ensure password is NOT in the simple UserSerializer
    #     self.assertNotIn('password', serializer.data)
