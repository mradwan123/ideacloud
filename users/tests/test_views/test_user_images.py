import os
import shutil
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from config.settings import MEDIA_ROOT, DEFAULT_PROFILE_IMAGE_URL, BASE_DIR
from config.image_helper.base64_image_conversion import image_to_base64
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.urls import reverse

User = get_user_model()

# Create a temporary directory for media files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

# we use @override_settings to overwrite the default MEDIA_ROOT
# this ensures that any files saved during testing go to our set TEMP_MEDIA_ROOT
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserProfileViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        """Clean up the entire temp media directory after all tests in this class are done"""
        super().tearDownClass()

        # check if the temp directory still exists on the disk
        if os.path.exists(TEMP_MEDIA_ROOT):
            # shutil.rmtree recursively deletes the directory and every file inside it
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='testuser',
                                             email='test@example.com',
                                             password='Testpass123',
                                             description='test desc')
        self.image_user_data = {'username': 'imgtestuser',
                                'email': 'imgtest@example.com',
                                'image': self._create_test_image(),
                                'password': 'Testpass123',
                                'description': 'test desc'}
        serializer = UserSerializer(data=self.image_user_data)
        serializer.is_valid()
        self.image_user = serializer.save()
        self.new_user_data = {'username': 'testuser2',
                              'email': 'test2@example.com',
                              'image': self._create_test_image(),
                              'password': 'Testpass123',
                              'description': 'test desc'}

        request = type('Request', (), {'user': self.user})()
        self.url = lambda user_id: reverse('users:user-detail', args=[user_id])
        self.url_users = reverse('users:user')

        self.client = APIClient()

        self.token_user = Token.objects.create(user=self.user)
        self.token_image_user = Token.objects.create(user=self.image_user)

    def _create_test_image(self):
        """Helper to create an image in memory"""
        # we create a 100x100px image in RAM
        image_path = MEDIA_ROOT / "profile_images" / "default.jpg"
        with open(image_path, "rb") as img:
            base64_image = image_to_base64(img.read())

        return base64_image

    def test_user_get_default_image_representaion(self):
        """Checks the correct respresentation of default image on GET request."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        response = self.client.get(self.url(self.user.id))

        self.assertEqual(response.data.get("image"), DEFAULT_PROFILE_IMAGE_URL)

    def test_user_get_custom_image_representaion(self):
        """Checks the correct respresentation of custom image on GET request."""
        serializer = UserSerializer(data=self.new_user_data)
        serializer.is_valid()
        new_user = serializer.save()
        new_token = Token.objects.create(user=new_user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {new_token}")
        response = self.client.get(self.url(new_user.id))

        img_response = response.data.get("image")
        self.assertNotEqual(img_response, DEFAULT_PROFILE_IMAGE_URL)
        self.assertTrue(img_response.startswith("/media/profile_images/image_"))
        self.assertTrue(img_response.endswith(".jpg"))

    def test_user_post_default_image_representaion(self):
        """Checks the correct respresentation of default image on POST request."""
        del self.new_user_data["image"]
        response = self.client.post(self.url_users, data=self.new_user_data, format="json")

        self.assertEqual(response.data.get("image"), DEFAULT_PROFILE_IMAGE_URL)

    def test_user_post_custom_image_representaion(self):
        """Checks the correct respresentation of custom image on POST request."""
        response = self.client.post(self.url_users, data=self.new_user_data, format="json")

        img_response = response.data.get("image")
        self.assertNotEqual(img_response, DEFAULT_PROFILE_IMAGE_URL)
        self.assertTrue(img_response.startswith("/media/profile_images/image_"))
        self.assertTrue(img_response.endswith(".jpg"))

    def test_user_put_default_image_representaion(self):
        """Checks the correct respresentation of default image after PUT request."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_image_user}")

        self.image_user_data["image"] = None
        response = self.client.put(self.url(self.image_user.id), data=self.image_user_data, format="json")

        self.assertEqual(response.data.get("image"), DEFAULT_PROFILE_IMAGE_URL)

    def test_user_put_custom_image_representaion(self):
        """Checks the correct respresentation of custom image after PUT request."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_image_user}")

        self.image_user_data["image"] = self._create_test_image()
        response = self.client.put(self.url(self.image_user.id), data=self.image_user_data, format="json")

        img_response = response.data.get("image")
        self.assertNotEqual(img_response, DEFAULT_PROFILE_IMAGE_URL)
        self.assertTrue(img_response.startswith("/media/profile_images/image_"))
        self.assertTrue(img_response.endswith(".jpg"))

    def test_user_patch_default_image_representaion(self):
        """Checks the correct respresentation of default image after PATCH request."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_image_user}")

        response = self.client.patch(self.url(self.image_user.id), data={"image": None}, format="json")

        self.assertEqual(response.data.get("image"), DEFAULT_PROFILE_IMAGE_URL)

    def test_user_patch_custom_image_representaion(self):
        """Checks the correct respresentation of custom image after PATCH request."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_image_user}")

        response = self.client.patch(self.url(self.image_user.id), data={"image": self._create_test_image()}, format="json")

        img_response = response.data.get("image")
        self.assertNotEqual(img_response, DEFAULT_PROFILE_IMAGE_URL)
        self.assertTrue(img_response.startswith("/media/profile_images/image_"))
        self.assertTrue(img_response.endswith(".jpg"))

    def test_user_delete_dete_image_file(self):
        """Checks if the custom image gets deleted from DB after account deletion."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_image_user}")

        image_path = self.image_user.image.path
        self.assertTrue(os.path.isfile(image_path))
        self.client.delete(self.url(self.image_user.id))
        self.assertFalse(os.path.isfile(image_path))
