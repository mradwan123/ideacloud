from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from projects.models import ImageProject, ProjectIdea
import os
from PIL import Image
from io import BytesIO
import shutil
import tempfile
from django.test import TestCase, override_settings
from django.urls import reverse

# Create a temporary media directory for tests
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageProjectTest(TestCase):

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
        return SimpleUploadedFile('view_test.jpg', buffer.read(), content_type='image/jpeg')

    def setUp(self):
        User = get_user_model()
        # create test user
        self.user = User.objects.create_user(username="author", password="password")

        # create test project_idea
        self.project_idea = ProjectIdea.objects.create(
            title="Test Idea",
            author=self.user,
            description="Descriptive text",
        )

    def test_image_upload(self):
        """
        Project images are uploaded to /project_images/. This test uses dummy files and test
        start of the path with project_images/test_image
        """
        # create dummy file
        dummy_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"fake image bytes",
            content_type="image/jpeg",)

        image_project = ImageProject.objects.create(project_idea=self.project_idea,
                                                    image=dummy_file)
        self.assertTrue(image_project.image.name.startswith('project_images/test_image'),)
        self.assertTrue(os.path.exists(image_project.image.path))

        # Checking foreign key
        self.assertIsNotNone(image_project.pk)
