from django.test import TestCase
from django.core.exceptions import ValidationError
# from users.models import User
from django.contrib.auth.models import User  # TODO remove this later and replace with line above
from ...models import ProjectGroup
from ...models import ProjectIdea
from django.db.utils import IntegrityError

class TestProjectGroup(TestCase):  

    def setUp(self):
        self.group_name = "test_group"
        self.group_description = "test description"
        self.password = "TestPassword1,"
        self.user = User.objects.create_user(username="test_user",
                                             password=self.password)
        self.project_idea = ProjectIdea.objects.create(title="test idea",
                                                       author=self.user,
                                                       description="test description",)    

    def test_models_project_group_create_group(self):
        """
        Test for creating a project group and validating the data.
        """
        
        group = ProjectGroup.objects.create(name=self.group_name,
                                            description=self.group_description,
                                            project_idea=self.project_idea,
                                            owner=self.user)
        
        self.assertIn(group, ProjectGroup.objects.all())
        self.assertEqual(group.name, self.group_name)
        self.assertEqual(group.description, self.group_description)
        self.assertEqual(group.owner, self.user)

    def test_models_project_group_unique_name(self):
        """
        Test for checking if the UniqueContraint for unique group name is triggered, when trying
        to create a new group under a project which has already a group with that name.
        """
        ProjectGroup.objects.create(name=self.group_name,
                                    description=self.group_description,
                                    project_idea=self.project_idea,
                                    owner=self.user)
        
        with self.assertRaises(IntegrityError):
            ProjectGroup.objects.create(name=self.group_name,
                                        description=self.group_description,
                                        project_idea=self.project_idea,
                                        owner=self.user)

    def test_models_project_group_name_too_long(self):
        """
        Test the contraint for too long group names.
        """

        group = ProjectGroup.objects.create(name="a" * 201,
                                            description=self.group_description,
                                            project_idea=self.project_idea,
                                            owner=self.user)
        with self.assertRaises(ValidationError):
            group.full_clean()

    def test_models_project_group_str_method(self):
        """
        Test to check if the str method is properly set up.
        """
        group = ProjectGroup.objects.create(name=self.group_name,
                                            description=self.group_description,
                                            project_idea=self.project_idea,
                                            owner=self.user)
        self.assertIn(f"Project Group: '{group.name}'", str(group))
