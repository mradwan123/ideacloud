from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from ...models import ImageProject, ProjectIdea
from django.db.utils import IntegrityError
    

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
        #create dummy file
        dummy_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"fake image bytes",
            content_type="image/jpeg",)
        
        
        image_project = ImageProject.objects.create(project_idea=self.project_idea,
                                                    image=dummy_file)                                     
        self.assertTrue(image_project.image.name.endswith('test_image.jpg'))
    
 
 