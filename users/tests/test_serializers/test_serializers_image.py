import os
import shutil
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer
from config.settings import MEDIA_ROOT, DEFAULT_PROFILE_IMAGE_URL
from config.image_helper.base64_image_conversion import image_to_base64

User = get_user_model()

# Create a temporary directory for media files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

# we use @override_settings to overwrite the default MEDIA_ROOT
# this ensures that any files saved during testing go to our set TEMP_MEDIA_ROOT
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserProfileSerializerTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        """Clean up the entire temp media directory after all tests in this class are done"""
        super().tearDownClass()

        # check if the temp directory still exists on the disk
        if os.path.exists(TEMP_MEDIA_ROOT):
            # shutil.rmtree recursively deletes the directory and every file inside it
            shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
            self.user_data = {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'testpass123',
                    'description':'test desc',
                }        
            

    def _create_test_image(self):
        """Helper to create an image in memory"""
        # we create a 100x100px image in RAM
        image_path = MEDIA_ROOT / "profile_images" / "default.jpg"
        with open(image_path, "rb") as img:
            base64_image = image_to_base64(img.read())
        
        return base64_image

    def test_user_image_base64_save_success_serialization(self):
        """Verify the serializer outputs the correct URL and ID"""
        image_file = self._create_test_image()
        data = self.user_data
        data['image'] = image_file

        # pass the database object into the serializer
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user_instance = serializer.save()

        # verify that the id in the JSON matches the id in the database
        self.assertEqual(serializer.data["id"], user_instance.id)

        # check if the string "test.jpg" exists in the "image" field so we know the path is correct
        self.assertTrue(serializer.data["image"].endswith(".jpg"))
        self.assertIn("/media/profile_images/image_", serializer.data["image"])
        self.assertTrue(os.path.isfile(user_instance.image.path))

    def test_user_image_default_representation(self):
        """Verify the serializer outputs the correct URL and ID"""
        data = self.user_data

        # pass the database object into the serializer
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user_instance = serializer.save()

        representaion = serializer.to_representation(user_instance)

        self.assertEqual(representaion.get("image"), DEFAULT_PROFILE_IMAGE_URL)

    def test_user_image_deletion_on_change(self):
        """Checks if custom profile image gets deleted from DB on account on user deletion."""
        image_file = self._create_test_image()
        data = self.user_data
        data['image'] = image_file

        # pass the database object into the serializer
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user_instance = serializer.save()

        img_path = user_instance.image.path
        self.assertTrue(os.path.isfile(img_path))

        updated_serializer = UserSerializer(user_instance, data={"image": self._create_test_image()}, partial=True)
        self.assertTrue(updated_serializer.is_valid())
        user_instance = updated_serializer.save()

        self.assertFalse(os.path.isfile(img_path))
        new_img_path = user_instance.image.path
        self.assertTrue(os.path.isfile(new_img_path))

    def test_user_image_deletion_on_set_to_null(self):
        """Checks if custom profile image gets deleted from DB on account on imagefield being set to null."""
        image_file = self._create_test_image()
        data = self.user_data
        data['image'] = image_file

        # pass the database object into the serializer
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user_instance = serializer.save()

        img_path = user_instance.image.path
        self.assertTrue(os.path.isfile(img_path))

        updated_serializer = UserSerializer(user_instance, data={"image": None}, partial=True)
        self.assertTrue(updated_serializer.is_valid())
        updated_user_instance = updated_serializer.save()

        self.assertFalse(os.path.isfile(img_path))

        representaion = serializer.to_representation(updated_user_instance)
        self.assertEqual(representaion.get("image"), DEFAULT_PROFILE_IMAGE_URL)

