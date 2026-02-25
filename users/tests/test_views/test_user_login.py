from django.test import TestCase
from django.contrib.auth import get_user_model
# from serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.urls import reverse

User = get_user_model()

class UserLoginTestAPIView(TestCase):
    """
    Docstring for UserTestAPIView:
    Creates setup with several users, admin, tokens, client, url.
    Test for login view with POST requests.
    
    """

    def setUp(self):

        # Setting up different users, different roles
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass1',
            email='test1@test.com',
        )
    
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass2',
            email='test2@test.com',
        )
    
        self.admin= User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@email.com'
       )
        
        #Set up user tokens
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        self.admin_token = Token.objects.create(user=self.admin) 

        self.client = APIClient()

        self.url = reverse('users:login')
        

    def test_login_success(self):
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        url= reverse('users:login')
        data = {
            'username':'testuser1',
            'password':'testpass1'
        }

        response =self.client.post(url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            msg=f"Expected 200, got {response.status_code}: {response.content}",
        )
    
    def test_login_missing_username(self):
        '''Regular user failing login attempt because no username given'''
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        url= reverse('users:login')
        data = {
            'username':'',
            'password':'testpass1'
        }

        response =self.client.post(url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=f"Expected 200, got {response.status_code}: {response.content}",
        )
        
    def test_login_missing_password_400(self):
        '''Regular user failing login attempt because no password'''
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        url= reverse('users:login')
        data = {
            'username':'username1',
            'password':''
        }

        response =self.client.post(url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=f"Expected 200, got {response.status_code}: {response.content}",
        )
        
    def test_login_no_token_401(self):
        '''No token, not authorized, should not be able to login. status 401.'''
        
        self.client.credentials()
        url= reverse('users:login')
        data = {
            'username':'username1',
            'password':'password1'
        }

        response =self.client.post(url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            msg=f"Expected 200, got {response.status_code}: {response.content}",
        )
        

