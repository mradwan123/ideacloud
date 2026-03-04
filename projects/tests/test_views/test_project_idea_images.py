from projects.models import ImageProject, ProjectIdea
from projects.serializers.serializer_image_project import ImageProjectSerializer
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from config.settings import MEDIA_ROOT
from config.image_helper.base64_image_conversion import image_to_base64
import os
import shutil
import tempfile
from rest_framework import status

User = get_user_model()

def create_test_image():
    """Helper to create an image in memory"""
    # we create a 100x100px image in RAM
    image_path = MEDIA_ROOT / "profile_images" / "default.jpg"
    # print(image_path)
    with open(image_path, "rb") as img:
        base64_image = image_to_base64(img.read())

    return base64_image

# Create a temporary directory for media files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

# we use @override_settings to overwrite the default MEDIA_ROOT
# this ensures that any files saved during testing go to our set TEMP_MEDIA_ROOT
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestAddProjectIdeaImage(TestCase):
    @classmethod
    def tearDownClass(cls):
        """Clean up the entire temp media directory after all tests in this class are done"""
        super().tearDownClass()

        # check if the temp directory still exists on the disk
        if os.path.exists(TEMP_MEDIA_ROOT):
            # shutil.rmtree recursively deletes the directory and every file inside it
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
    
    def setUp(self):
        self.user = User.objects.create_user(username="test_user",
                                             email="test_user@email.com",
                                             password="TestPassword1,")
        self.user2 = User.objects.create_user(username="test_user2",
                                              email="test_user2@email.com",
                                              password="TestPassword1,")
        self.project_idea = ProjectIdea.objects.create(title="test idea",
                                                       author=self.user,
                                                       description="test description",)
        self.url = lambda idea_pk: reverse('projects:project-idea-add-image', args=[idea_pk])
        self.client = APIClient()

        self.token_user = Token.objects.create(user=self.user)
        self.token_user2 = Token.objects.create(user=self.user2)

    def test_project_idea_images_post_add_valid_image(self):
        """Authorized user creates a valid image and validates its db entry."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")

        data = {"image": create_test_image()}
        response = self.client.post(self.url(self.project_idea.id), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data.keys())
        self.assertIn('image', response.data.keys())
        url = response.data.get("image")
        self.assertTrue(url.endswith(".jpg"))
        self.assertTrue(url.startswith("/media/project_images/image_"))

    def test_project_idea_images_post_add_invalid_user(self):
        """Unauthorized user tries to create valid image. Validates error response."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user2}")

        data = {"image": create_test_image()}
        response = self.client.post(self.url(self.project_idea.id), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data.keys())

    def test_project_idea_images_post_add_invalid_project_idea(self):
        """User tries to create valid image under non existing project idea. Validates error response."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")

        data = {"image": create_test_image()}
        response = self.client.post(self.url(9999999999999), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data.keys())

    def test_project_idea_images_post_add_invalid_image(self):
        """Authorized user tries to create invalid image. Validates error response."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")

        data = {"image": "image of a tree"}
        response = self.client.post(self.url(self.project_idea.id), data=data, format="json")

        self.assertIn("image", response.data.keys())
        self.assertEqual(response.data.get("image")[0].code, "invalid_image")

# we use @override_settings to overwrite the default MEDIA_ROOT
# this ensures that any files saved during testing go to our set TEMP_MEDIA_ROOT
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestRemoveProjectIdeaImage(TestCase):
    @classmethod
    def tearDownClass(cls):
        """Clean up the entire temp media directory after all tests in this class are done"""
        super().tearDownClass()

        # check if the temp directory still exists on the disk
        if os.path.exists(TEMP_MEDIA_ROOT):
            # shutil.rmtree recursively deletes the directory and every file inside it
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username="test_user",
                                             email="test_user@email.com",
                                             password="TestPassword1,")
        self.user2 = User.objects.create_user(username="test_user2",
                                              email="test_user2@email.com",
                                              password="TestPassword1,")
        self.project_idea = ProjectIdea.objects.create(title="test idea",
                                                       author=self.user,
                                                       description="test description",)
        self.project_idea2 = ProjectIdea.objects.create(title="test idea2",
                                                        author=self.user2,
                                                        description="test description2",)

        self.url = lambda idea_pk: reverse('projects:project-idea-remove-image', args=[idea_pk])
        self.client = APIClient()

        self.token_user = Token.objects.create(user=self.user)
        self.token_user2 = Token.objects.create(user=self.user2)

        image_serialzer = ImageProjectSerializer(data={"image": create_test_image(),
                                                       "project_idea": self.project_idea.id})
        image_serialzer.is_valid()
        self.image_instance = image_serialzer.save()

        image_serialzer2 = ImageProjectSerializer(data={"image": create_test_image(),
                                                        "project_idea": self.project_idea2.id})
        image_serialzer2.is_valid()
        self.image_instance2 = image_serialzer2.save()

    def test_project_idea_images_delete_remove_image(self):
        """Authorized user deletes image and validates its deletion from db."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"image_id": self.image_instance.id}
        image_id = self.image_instance.id

        disk_path = os.path.join(TEMP_MEDIA_ROOT, self.image_instance.image.name)
        self.assertTrue(os.path.exists(disk_path))
        self.assertTrue(ImageProject.objects.filter(id=image_id).exists())

        response = self.client.delete(self.url(self.project_idea.id), data=data, format="json")
        
        self.assertFalse(os.path.exists(disk_path))
        self.assertFalse(ImageProject.objects.filter(id=image_id).exists())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data.keys())

    def test_project_idea_images_delete_invalid_project_idea(self):
        """User tries to delete image of non existing project idea. Validates error response."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"image_id": self.image_instance.id}

        response = self.client.delete(self.url(99999999), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data.keys())

    def test_project_idea_images_delete_unauthorized_user(self):
        """Unauthorized user tries to delete image from project idea. Validates error response."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user2}")
        data = {"image_id": self.image_instance.id}

        response = self.client.delete(self.url(self.project_idea.id), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data.keys())

    def test_project_idea_images_delete_invalid_image_id(self):
        """Authorized user tries to delete image from project idea with invalid image id. Validates error response."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"image_id": 99999999999}

        response = self.client.delete(self.url(self.project_idea.id), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data.keys())

    def test_project_idea_images_delete_missing_image_id(self):
        """Authorized user tries to delete image from project idea missing image id. Validates error response."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"image_id": self.image_instance2.id}

        response = self.client.delete(self.url(self.project_idea.id), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data.keys())
