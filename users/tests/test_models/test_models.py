from django.test import TestCase, override_settings
from ...models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import os    
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile


# Create a temporary media directory for tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserModelTest(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
            
    def _create_test_image(self):
        """Helper to create a temporary image file"""
        image = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        return SimpleUploadedFile('profile_test.jpg', buffer.read(), content_type='image/jpeg')
    
    #TODO change create to create user and make tests pass
    def setUp(self):
        self.user = User.objects.create(
            username = 'testusername',
            email = 'something@ideacloud.com',
            password = 'idea123',
            description = 'some texts',
            created_on = '2026-02-19',
            available = False
            )
    
        
    #---- VALIDATION --------------
        self.assertEqual(self.user.username, 'testusername')
        self.assertEqual(self.user.email, 'something@ideacloud.com')
        self.assertEqual(self.user.password, 'idea123')
        self.assertEqual(self.user.description, 'some texts')
        self.assertEqual(self.user.available, False)
        
    def test_User_created_on_correct_timestamp(self):
        """Verify that timestamps are generated correctly"""
        self.assertIsNotNone(self.user.created_on)
        now = timezone.now()
        # we use AlmostEqual, because we can't compare accurately on a detailed level because the code takes time to run
        self.assertAlmostEqual(
            self.user.created_on,
            now,
            delta=timedelta(minutes=1)
        )
        
    def test__user_password_hashing(self):        
        user = User.objects.create_user(username='bob', password='plain')
        self.assertNotEqual(user.password, 'plain')
        self.assertTrue(user.check_password('plain'))   
        
    def test_user_create_date_is_wrong_format(self):
          with self.assertRaises(ValidationError):
            user = User(created_on='12-12-12')
            user.full_clean()

    def test_user_default_image_path(self):
        default_path = str(settings.MEDIA_ROOT) + "/profile_images/default.jpg"
        user_path = self.user.image.path
        self.assertEqual(default_path, user_path)

    def test_user_custom_image_path(self):
        new_profile_image = self._create_test_image()
        new_user = User.objects.create_user(username='test_image_user',
                                   email='test_image_user@ideacloud.com',
                                   password='idea123',
                                   image=new_profile_image,
                                   description='some texts',
                                   created_on='2026-02-19',
                                   available=False)
        default_path = str(settings.MEDIA_ROOT) + "/profile_images/profile_test"
        user_path = new_user.image.path
        self.assertIn(default_path, user_path)
            
    def test_username_unique_constraint(self): #Abstractuser class includes by default unique username
        User.objects.create_user(username='george', email='a@locospace.com', password='password')
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='george', email='g@locospace.com', password='password')

    
    def test_email_not_unique_constraint(self): #Abstractuser class does NOT include by default unique email
        '''Testing two users with same email. Test passes as per built in Abstract user constraints'''
        User = get_user_model()
        user1 = User.objects.create_user(username='george', email='george@gmail.com', password='password')
        user2 = User.objects.create_user(username='radwan', email='george@gmail.com', password='password')
        self.assertEqual(user1.email, user2.email)
        
    
    def test_user_email_blank(self): #Abstractuser class includes by default unique email = blank
        '''Shows how email can be blank. '''
        User = get_user_model()
        user = User.objects.create_user(username='george', password='p')
        self.assertFalse(user.email, None)
        
        