from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from ...models import ImageProject, ProjectIdea
import os    

class ImageProjectTest(TestCase):
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
        #create dummy file
        dummy_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"fake image bytes",
            content_type="image/jpeg",)
        
        
        image_project = ImageProject.objects.create(project_idea=self.project_idea,
                                                    image=dummy_file)                                     
        self.assertTrue(image_project.image.name.startswith('project_images/test_image'),)
        self.assertTrue(os.path.exists(image_project.image.path))
        
        #Checking foreign key
        self.assertIsNotNone(image_project.pk)



   

 