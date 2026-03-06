from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from projects.models import FinishedProject, Tag, ProjectIdea, ProjectGroup

User = get_user_model()

class FinishedProjectsListTests(APITestCase):
    def setUp(self):
        # create users
        self.user1 = User.objects.create_user(username="user1", password="password", email="user1@email.com")
        self.user2 = User.objects.create_user(username="user2", password="password", email="user2@email.com")
        # create tags
        self.tag_python = Tag.objects.create(name="python")
        self.tag_automation = Tag.objects.create(name="automation")
        # create project ideas
        self.project_idea = ProjectIdea.objects.create(
            title="Project Idea",
            description="Testing views",
            author=self.user1
        )
        # create a group
        self.project_group = ProjectGroup.objects.create(
            name='Test Group',
            project_idea=self.project_idea,
            owner=self.user1  # TODO create another user that is not project idea owner, and is group owner
        )

        # create a finished project
        self.finished_project = FinishedProject.objects.create(
            title="Finished Project Title",
            description="Testing views",
            project_group=self.project_group
        )
        # adding "python" tag to the finished project
        self.finished_project.tags.add(self.tag_python)
        # helpers to manage urls easier in test
        self.url_list = reverse("projects:finished-project-list")

    ### VALID
    ## GET
    def test_get_all_finished_projects(self):
        """
        Verify that anyone can see all project ideas
        Also verify that data structure stays intact so we don't have to test for it every test
        """
        # make sure we are not logged in
        self.client.logout()
        # creating additional project
        finished_project_2 = FinishedProject.objects.create(
            title="Finished Project Title",
            description="Testing views",
            project_group=self.project_group
        )

        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # we use 1 here as the view returns in reverse order sorted by creation time and our setup finished_project comes second in this order
        # this also verifies that the default sorting is working as intended
        finished_project = response.data[1]

        # verify base fields
        self.assertEqual(finished_project["title"], "Finished Project Title")
        self.assertEqual(finished_project["description"], "Testing views")

        # verify nested M2M data
        finished_project = response.data[0]

        self.assertIn("python", finished_project["tags"])

        # verify annotated fields
        # self.assertEqual(finished_project["likes_count"], 0)
        # self.assertEqual(finished_project["has_liked"], False)

    ## POST
    def test_create_finished_project_authenticated_user(self):
        """Verify that a logged in user can create a ProjectIdea"""
        self.client.force_authenticate(user=self.user1)

        data = {
            "title": "Entirely new idea",
            "description": "Entirely new description",
            "tags": ["automation"],
            "project_group": self.project_group.id
        }
        response = self.client.post(self.url_list, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FinishedProject.objects.count(), 2)

    ### INVALID
    ## POST
    def test_create_finished_project_unauthenticated(self):
        """Ensures that guests cannot create new projects"""
        self.client.logout()

        data = {
            "title": "Entirely new idea",
            "description": "Entirely new description",
            "tags": ["automation"],
            "project_group": self.project_group.id
        }
        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_finished_project_invalid_data(self):
        """Confirms that projects with bad data aren't created"""
        self.client.force_authenticate(user=self.user1)

        data = {
            "title": "idea",
            "description": "Entirely new description",
        }

        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class FinishedProjectDetailTests(APITestCase):
    def setUp(self):
        # create users
        self.user1 = User.objects.create_user(username="user1", password="password", email="user1@email.com")
        self.user2 = User.objects.create_user(username="user2", password="password", email="user2@email.com")
        # create tags
        self.tag_python = Tag.objects.create(name="python")
        self.tag_automation = Tag.objects.create(name="automation")
        # create project ideas
        self.project_idea = ProjectIdea.objects.create(
            title="Project Idea",
            description="Testing views",
            author=self.user1
        )
        self.project_group = ProjectGroup.objects.create(
            name='Test Group',
            project_idea=self.project_idea,
            owner=self.user1  # TODO create another user that is not project idea owner, and is group owner
        )
        # create finsihed project
        self.finished_project = FinishedProject.objects.create(
            title="Finished Project Title",
            description="Testing views",
            project_group=self.project_group
        )

        # adding "python" tag to the finished_project
        self.finished_project.tags.add(self.tag_python)
        # helpe to manage urls easier in test
        self.url_detail = reverse("projects:finished-project-detail", kwargs={"finished_pk": self.finished_project.pk})

    ### VALID
    ## GET
    def test_get_a_single_finished_project(self):
        """
        Verify that anyone can see a project idea by id
        """
        # make sure we are not logged in
        self.client.logout()

        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # verify any field
        self.assertEqual(response.data["title"], "Finished Project Title")

    # PATCH #TODO for project_group.owner no author
    def test_update_a_single_finished_project_as_group_owner_no_likes(self):
        """Test that an author can edit their finsihed project before it has likes or groups attached"""
        self.client.force_authenticate(user=self.user1)

        data = {
            "title": "Entirely New Idea",
            "description": "Entirely new description",
            "tags": ["automation"],
            "project_group": self.project_group.id
        }
        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], data["title"])

    ## DELETE

    def test_delete_finished_project_as_author(self):
        """Verifies that the project group owner can delete the finished project"""
        self.client.force_authenticate(user=self.user1)

        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    ### INVALID
    ## PATCH
    # def test_update_a_non_existing_finished_project(self):
    #     """Test that an author can edit their project idea before it has likes or groups attached"""
    #     self.client.force_authenticate(user=self.user1)

    #     url_non_existing_idea = reverse('projects:finished-project-detail', kwargs={'finished_pk': 999999})
    #     data = {"title": "Non Existing Finnished Project Title"}
    #     response = self.client.patch(url_non_existing_idea, data, format="json")

    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #     self.assertIs(response.data.get("title"), None)

    # TODO determine if similar test as below is necessary and implement accordingly. Current: Test error.
    def test_update_a_single_finished_project_as_guest(self):
        """Test that an owner can edit their final project before it has likes or groups attached"""
        self.client.logout()

        data = {
            "title": "Great New Idea",
            "description": "Entirely new description",
            "tags": ["automation"],
            "project_group": self.project_group.id
        }
        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIs(response.data.get("title"), None)

    def test_update_a_single_finished_project_as_other_user(self):
        """Test that an author can edit their project idea before it has likes or groups attached"""
        self.client.force_authenticate(user=self.user2)

        data = {
            "title": "Great New Idea",
            "description": "Entirely new description",
            "tags": ["automation"],
            "project_group": self.project_group.id
        }
        response = self.client.patch(self.url_detail, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("User is not allowed to edit description/title of this Finished Group.", str(response.data))

    ## DELETE
    def test_delete_finished_project_as_guest(self):
        """Ensures that a a guest cannot update a finished project's content"""
        self.client.logout()

        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_finished_project_as_other_user(self):
        """Ensures that another user that is not the author of a finished project cannot delete it"""
        self.client.force_authenticate(user=self.user2)

        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    ## SERIALIZER CONNECTION
    def test_update_finished_project_with_profane_content(self):
        """Makes sure that the view rejects banned words correctly (via serializer)"""
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "Fuck Great New Idea",
            "description": "Entirely new description",
            "tags": ["automation"],
            "project_group": self.project_group.id
        }

        response = self.client.patch(self.url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertIn("Profanity", str(response.data))
