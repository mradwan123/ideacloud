from django.test import TestCase
from django.core.exceptions import ValidationError
from ...models import ProjectGroup

class TestProjectGroup(TestCase):
    
    def setUp(self):
        self.group_name = "test_group"
        self.group_description = "test description"
        self.password = "TestPassword1,"
        # self_project_idea = ProjectIdea(
        #                                 title="A" * 201,
        #                                 author=self.user,
        #                                 description="Descriptive text",
        #                                 )
        # # self.user = User.objects.create_user(username="test",
        #                                       email="test@email.com",
        #                                       password=self.password)

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
        
        with self.assertRaises(ValidationError):
            ProjectGroup.objects.create(name=self.group_name,
                                            description=self.group_description,
                                            project_idea=self.project_idea,
                                            owner=self.user)
        #self.assertEqual(type(e.exception), ValidationError)

    def test_models_project_group_name_too_long(self):

        with self.assertRaises(ValidationError):
            ProjectGroup.objects.create(name="a"*300,
                                            description=self.group_description,
                                            project_idea=self.project_idea,
                                            owner=self.user)


    def test_models_project_group_unique_name(self):
        """
        Test for chekcing if a created group can be deleted from the table.
        """

        group = ProjectGroup.objects.create(name=self.group_name,
                                            description=self.group_description,
                                            project_idea=self.project_idea,
                                            owner=self.user)

        self.assertIn(group, ProjectGroup.objects.all())
        group.delete()
        self.assertNotIn(group, ProjectGroup.objects.all())
