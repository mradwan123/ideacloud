from django.test import TestCase
from ...models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.conf import settings



class UserModelTest(TestCase):
    
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
        
        