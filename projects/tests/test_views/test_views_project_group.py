from django.test import TestCase
from django.core.exceptions import ValidationError
from projects.serializers.serializer_project_group_serializer import ProjectGroupSerializer
from projects.views.view_project_group import ProjectGroupDetail, ProjectGroupList
from projects.models import ProjectIdea, ProjectGroup
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


class TestProjectGroupListView(TestCase):
    """Test cases for the ProjectGroupList view."""

    def setUp(self):
        User = get_user_model()
        self.group_description = "test description"
        self.password = "TestPassword1,"
        self.user = User.objects.create_user(username="test_user",
                                             email="test_user@email.com",
                                             password=self.password)
        self.user2 = User.objects.create_user(username="test_user2",
                                              email="test_user2@email.com",
                                              password=self.password)
        self.project_idea = ProjectIdea.objects.create(title="test idea",
                                                       author=self.user,
                                                       description="test description",)
        self.project_group1 = ProjectGroup.objects.create(name="test_group1",
                                                          description=self.group_description,
                                                          project_idea=self.project_idea,
                                                          owner=self.user)
        self.project_group2 = ProjectGroup.objects.create(name="test_group2",
                                                          description=self.group_description,
                                                          project_idea=self.project_idea,
                                                          owner=self.user2)
        self.project_group_data = {"name": "test group",
                                   "description": "test description"}
        request = type('Request', (), {'user': self.user})()
        self.context = {"request": request,
                        "project_idea": self.project_idea}
        self.url = lambda idea_pk: reverse('projects:project-group-list', args=[idea_pk])
        self.client = APIClient()

        self.token_user = Token.objects.create(user=self.user)
        self.token_user2 = Token.objects.create(user=self.user2)
    
    def test_view_get_project_group_list_valid(self):
        """Test retrieving all project groups for a valid project idea."""
        response = self.client.get(self.url(self.project_idea.id))
        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)
        name_list = [x.get("name") for x in data]
        description_list = [x.get("description") for x in data]
        project_idea_list = [x.get("project_idea") for x in data]
        owner_list = [x.get("owner").get("username") for x in data]
        self.assertIn(self.project_group1.name, name_list)
        self.assertIn(self.project_group1.description, description_list)
        self.assertIn(self.project_group1.project_idea.id, project_idea_list)
        self.assertIn(self.project_group1.owner.username, owner_list)
        self.assertIn(self.project_group2.name, name_list)
        self.assertIn(self.project_group2.description, description_list)
        self.assertIn(self.project_group2.project_idea.id, project_idea_list)
        self.assertIn(self.project_group2.owner.username, owner_list)

    def test_view_get_project_group_list_invalid_project_idea(self):
        """Test retrieving project groups with a non-existent project idea ID."""
        response = self.client.get(self.url(999999999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_post_project_group_list_create(self):
        """Test creating a new project group with valid authentication."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"name": "new_group",
                "description": "new description"}
        response = self.client.post(self.url(self.project_idea.id), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(data.get("name"), response.data.get("detail"))

    def test_view_post_project_group_list_invalid_token(self):
        """Test creating a project group with an invalid authentication token."""
        self.client.credentials(HTTP_AUTHORIZATION=f"{self.token_user}")

        data = {"name": "new_group",
                "description": "new description"}
        response = self.client.post(self.url(self.project_idea.id), data=data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data.get("detail").code, "not_authenticated")

class TestProjectGroupDetailView(TestCase):
    """Test cases for the ProjectGroupDetail view."""
    def setUp(self):
        User = get_user_model()
        self.group_name = "test_group"
        self.group_description = "test description"
        self.password = "TestPassword1,"
        self.user = User.objects.create_user(username="test_user",
                                             email="test_user@email.com",
                                             password=self.password)
        self.user2 = User.objects.create_user(username="test_user2",
                                              email="test_user2@email.com",
                                              password=self.password)
        self.project_idea = ProjectIdea.objects.create(title="test idea",
                                                       author=self.user,
                                                       description="test description",)
        self.project_group = ProjectGroup.objects.create(name=self.group_name,
                                                         description=self.group_description,
                                                         project_idea=self.project_idea,
                                                         owner=self.user)
        self.project_group_data = {"name": "test group",
                                   "description": "test description"}
        request = type('Request', (), {'user': self.user})()
        self.context = {"request": request,
                        "project_idea": self.project_idea}
        self.url = lambda idea_pk, group_pk: reverse('projects:project-group-detail', args=[idea_pk, group_pk])
        self.client = APIClient()

        self.token_user = Token.objects.create(user=self.user)
        self.token_user2 = Token.objects.create(user=self.user2)

    def test_view_get_project_group_detail_valid(self):
        """Test retrieving a specific project group with valid IDs."""
        response = self.client.get(self.url(self.project_idea.id, self.project_group.id))

        data = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("id"), self.project_group.id)
        self.assertEqual(data.get("name"), self.project_group.name)
        self.assertEqual(data.get("description"), self.project_group.description)
        self.assertEqual(data.get("project_idea"), self.project_group.project_idea.id)
        self.assertEqual(data.get("owner").get("username"), self.project_group.owner.username)

    def test_view_get_project_group_detail_invalid_project_idea(self):
        """Test retrieving a project group with an invalid project idea ID."""
        response = self.client.get(self.url(999999999, self.project_group.id))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_get_project_group_detail_invalid_project_group(self):
        """Test retrieving a project group with an invalid group ID."""
        response = self.client.get(self.url(self.project_idea.id, 99999999999))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_put_project_group_detail_valid(self):
        """Test fully updating a project group with valid data."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"name": "updated_name",
                "description": "updated description"}
        response = self.client.put(self.url(self.project_idea.id, self.project_group.id), data=data, format="json")

        self.assertEqual(data.get("name"), response.data.get("name"))
        self.assertEqual(data.get("description"), response.data.get("description"))

    def test_view_put_project_group_detail_name_missing(self):
        """Test fully updating a project group without providing a name."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"description": "updated description"}
        response = self.client.put(self.url(self.project_idea.id, self.project_group.id), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data.keys())

    def test_view_put_project_group_detail_description_missing(self):
        """Test fully updating a project group without providing a description."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"name": "updated_name"}
        response = self.client.put(self.url(self.project_idea.id, self.project_group.id), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data.keys())

    def test_view_patch_project_group_detail_valid_name(self):
        """Test partially updating only the name of a project group."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"name": "updated_name"}
        response = self.client.patch(self.url(self.project_idea.id, self.project_group.id), data=data, format="json")

        self.assertEqual(data.get("name"), response.data.get("name"))
        self.assertEqual(self.project_group.description, response.data.get("description"))

    def test_view_patch_project_group_detail_valid_description(self):
        """Test partially updating only the description of a project group."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"description": "updated description"}
        response = self.client.patch(self.url(self.project_idea.id, self.project_group.id), data=data, format="json")

        self.assertEqual(data.get("description"), response.data.get("description"))
        self.assertEqual(self.project_group.name, response.data.get("name"))

    def test_view_patch_project_group_detail_invalid_group(self):
        """Test partially updating a project group with an invalid group ID."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        data = {"description": "updated description"}
        response = self.client.patch(self.url(self.project_idea.id, 99999999999999999), data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_view_patch_project_group_detail_valid_delete(self):
        """Test deleting a project group with valid authentication."""
        project_group_id = self.project_group.id
        self.assertTrue(ProjectGroup.objects.filter(id=project_group_id).exists())

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token_user}")
        response = self.client.delete(self.url(self.project_idea.id, self.project_group.id))
        self.assertFalse(ProjectGroup.objects.filter(id=project_group_id).exists())
        self.assertIn("deleted.", response.data.get("detail"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

