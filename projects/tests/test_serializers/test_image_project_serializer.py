import os
import shutil
import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from PIL import Image
from io import BytesIO
from projects.models import ProjectIdea, ImageProject
from projects.serializers.serializer_image_project import ImageProjectSerializer
from config.settings import MEDIA_ROOT
from config.image_helper.base64_image_conversion import image_to_base64

User = get_user_model()

# Create a temporary directory for media files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

# we use @override_settings to overwrite the default MEDIA_ROOT
# this ensures that any files saved during testing go to our set TEMP_MEDIA_ROOT
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageProjectSerializerTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        """Clean up the entire temp media directory after all tests in this class are done"""
        super().tearDownClass()

        # check if the temp directory still exists on the disk
        if os.path.exists(TEMP_MEDIA_ROOT):
            # shutil.rmtree recursively deletes the directory and every file inside it
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username="test_dev", password="password")
        self.project_idea = ProjectIdea.objects.create(
            title="Test Project",
            author=self.user,
            description="Testing image serialization"
        )

    def _create_test_image(self):
        """Helper to create an image in memory"""
        # we create a 100x100px image in RAM
        image_path = MEDIA_ROOT / "profile_images" / "default.jpg"
        # print(image_path)
        with open(image_path, "rb") as img:
            base64_image = image_to_base64(img.read())
        
        return base64_image

    def test_image_serialization_output(self):
        """Verify the serializer outputs the correct URL and ID"""
        image_file = self._create_test_image()
        # image_instance = ImageProject.objects.create(
        #     project_idea=self.project_idea,
        #     image=image_file
        # )
        data = {"image": image_file,
                "project_idea": self.project_idea.id}

        # pass the database object into the serializer
        serializer = ImageProjectSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        image_instance = serializer.save()

        # verify that the id in the JSON matches the id in the database
        self.assertEqual(serializer.data["id"], image_instance.id)

        # check if the string "test.jpg" exists in the "image" field so we know the path is correct
        self.assertTrue(serializer.data["image"].endswith(".jpg"))
        self.assertIn("/media/project_images/image_", serializer.data["image"])
        # verify the project_idea is returned as its ID (the primary key)
        self.assertEqual(image_instance.project_idea.id, self.project_idea.id)

    def test_image_deserialization_and_save(self):
        """
        We simulate a user uploading a file through an API and check if the
        serializer handles the validation and file storage correctly
        """
        # raw data as if it just came from a POST request
        # 'image_file' here is in RAM
        image_file = self._create_test_image()
        data = {
            "project_idea": self.project_idea.id,
            "image": image_file
        }

        # triggers to_internal_value() and validation logic.
        serializer = ImageProjectSerializer(data=data)

        # check if there's any errors
        self.assertTrue(serializer.is_valid(), serializer.errors)

        # this creates a record in the database and triggers django to move the file from RAM to the TEMP_MEDIA_ROOT
        image_instance = serializer.save()

        # check that the model instance was actually created in the db
        self.assertEqual(ImageProject.objects.count(), 1)
        self.assertEqual(image_instance.project_idea, self.project_idea)

        # we construct the expected path on the 'hard drive' and check if the file exists there
        disk_path = os.path.join(TEMP_MEDIA_ROOT, image_instance.image.name)
        # second value is the error, if assesment is not true
        self.assertTrue(os.path.exists(disk_path), f"File was not found at {disk_path}")
