from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from django.urls import reverse
from config.settings import MEDIA_ROOT
from config.image_helper.base64_image_conversion import image_to_base64
import os
import shutil
import tempfile

User = get_user_model()

# Create a temporary directory for media files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

# we use @override_settings to overwrite the default MEDIA_ROOT
# this ensures that any files saved during testing go to our set TEMP_MEDIA_ROOT
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserTestAPIView(TestCase):
    """
    Docstring for UserTestAPIView:
    Creates setup with several users, admin, tokens, client, url.
    Test for GET/POST requests.
    """
    @classmethod
    def tearDownClass(cls):
        """Clean up the entire temp media directory after all tests in this class are done"""
        super().tearDownClass()

        # check if the temp directory still exists on the disk
        if os.path.exists(TEMP_MEDIA_ROOT):
            # shutil.rmtree recursively deletes the directory and every file inside it
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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

        self.url = reverse('users:user')
        
    def _create_test_image(self):
        """Helper to create a user profile image in memory"""
        # we create a 100x100px image in RAM
        image_path = MEDIA_ROOT / "profile_images" / "default.jpg"
        with open(image_path, "rb") as img:
            base64_image = image_to_base64(img.read())
        
        return base64_image

    def test_users_get_list_as_admin_successful(self):
        """Admin can retrieve the full user list with all details."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_users_get_list_as_user_fail(self):
        """Users cannot retrieve the full user list with all details."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token1.key}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_post_request_create_user_successful(self):
        data = {
            'username':'testuser4',
            'password':'Tpassword123',
            'email': 'test3@test.com',
            'description': 'test desc',
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('testuser4', str(response.data['username']))
        self.assertEqual('test3@test.com', str(response.data['email']))
        self.assertEqual('test desc', str(response.data['description']))
        
    def test_failed_user_register_with_post_request_authentication_no_username(self):
        'User to add account with post request with no authentication but no username. Should fail with 400.'

        data = {
            # 'username':'testuser4', removed for test
            'password':'Tpassword123',
            'email': 'test3@test.com',
            'description': 'test desc'
        }
        
        response =self.client.post(self.url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=f"Expected 400, got {response.status_code}: {response.content}",
        )
        # self.assertIn('username', response.data)
        # self.assertIn("required", str(response.data['username']))

    def test_failed_user_register_with_post_request_authentication_no_password(self):
        'User to add account with post request with no authentication but no password. Should fail with 400.'

        data = {
            'username':'testuser4', 
            # 'password':'Tpassword123', removed for test
            'email': 'test3@test.com',
            'description': 'test desc'
        }
        
        response =self.client.post(self.url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=f"Expected 400, got {response.status_code}: {response.content}",
        )
   
        
    def test_failed_user_register_with_post_request_authentication_no_email(self):
        'User to add account with post request with no authentication but no email. Should fail with 400.'

        data = {
            'username':'testuser4', 
            'password':'Tpassword123', 
            # 'email': 'test3@test.com', removed for test
            'description': 'test desc'
        }
        
        response =self.client.post(self.url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=f"Expected 400, got {response.status_code}: {response.content}",
        )
   
    def test_failed_user_register_with_post_request_authentication_no_description(self):
        'User to add account with post request with no authentication but no description. Should fail with 400.'

        data = {
            'username':'testuser4', 
            'password':'Tpassword123', 
            'email': 'test3@test.com', 
            #'description': 'test desc', removed for test
        }
        
        response =self.client.post(self.url, data, format='json')

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            msg=f"Expected 400, got {response.status_code}: {response.content}",
        )

    def test_post_create_user_with_image_base64_successful(self):
        data = {
            'username':'testuser4',
            'password':'Tpassword123',
            'email': 'test3@test.com',
            'description': 'test desc',
            'image': self._create_test_image()
        }
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)