from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from projects.models import ProjectIdea, Tag

User = get_user_model()

class ProjectIdeaListTests(APITestCase):
    def setUp(self):
        # create users
        self.user_author = User.objects.create_user(username="author", password="password", email="author@email.com")
        self.user_other = User.objects.create_user(username="other", password="password", email="other@email.com")
        # create tags
        self.tag_python = Tag.objects.create(name="python")
        self.tag_automation = Tag.objects.create(name="automation")
        # create project ideas
        self.project_idea = ProjectIdea.objects.create(
            title="Project Idea",
            description="Testing views",
            author=self.user_author
        )
        # adding "python" tag to the project_idea
        self.project_idea.tags.add(self.tag_python)
        # helpers to manage urls easier in test
        self.url_list = reverse("projects:project-idea-list")

    ### VALID
    ## GET
    def test_get_all_project_ideas(self):
        """
        Verify that anyone can see all project ideas
        Also verify that data structure stays intact so we don't have to test for it every test
        """
        # make sure we are not logged in
        self.client.logout()
        # creating additional project
        project_idea_2 = ProjectIdea.objects.create(
            title="Project Idea 2",
            description="Testing views 2",
            author=self.user_author
        )

        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # we use 1 here as the view returns in reverse order sorted by creation time and our setup project_idea comes second in this order
        # this also verifies that the default sorting is working as intended
        idea = response.data[1]
        # verify base fields
        self.assertEqual(idea["title"], "Project Idea")
        self.assertEqual(idea["description"], "Testing views")
        self.assertEqual(idea["author"], self.user_author.username)

        # verify nested M2M data
        self.assertIn("python", idea["tags"])
        self.assertIsInstance(idea["images_projects"], list)
        self.assertIsInstance(idea["project_idea_comments"], list)

        # verify annotated fields
        self.assertEqual(idea["likes_count"], 0)
        self.assertEqual(idea["has_liked"], False)

    ## POST
    def test_create_project_idea_authenticated_user(self):
        """Verify that a logged in user can create a ProjectIdea"""
        self.client.force_authenticate(user=self.user_author)

        data = {
            "title": "Entirely new idea",
            "description": "Entirely new description",
            "tags": ["automation"]
        }
        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProjectIdea.objects.count(), 2)

    ### INVALID
    ## POST
    def test_create_project_idea_unauthenticated(self):
        """Ensures that guests cannot create new projects"""
        self.client.logout()

        data = {
            "title": "Entirely new idea",
            "description": "Entirely new description",
            "tags": ["automation"]
        }
        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_project_idea_invalid_data(self):
        """Confirms that projects with bad data aren't created"""
        self.client.force_authenticate(user=self.user_author)

        data = {
            "title": "idea",
            "description": "Entirely new description",
        }

        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProjectIdeaDetailTests(APITestCase):
    def setUp(self):
        # create users
        self.user_author = User.objects.create_user(username="author", password="password", email="author@email.com")
        self.user_other = User.objects.create_user(username="other", password="password", email="other@email.com")
        # create tags
        self.tag_python = Tag.objects.create(name="python")
        self.tag_automation = Tag.objects.create(name="automation")
        # create project ideas
        self.project_idea = ProjectIdea.objects.create(
            title="Project Idea",
            description="Testing views",
            author=self.user_author
        )
        # adding "python" tag to the project_idea
        self.project_idea.tags.add(self.tag_python)
        # helpe to manage urls easier in test
        self.url_detail = reverse("projects:project-idea-detail", kwargs={"idea_pk": self.project_idea.pk})

    ### VALID
    ## GET
    def test_get_a_single_project_idea(self):
        """
        Verify that anyone can see a project idea by id
        """
        # make sure we are not logged in
        self.client.logout()

        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # verify any field
        self.assertEqual(response.data["title"], "Project Idea")

    ## PATCH
    def test_update_a_single_project_idea_as_author_no_likes(self):
        """Test that an author can edit their project idea before it has likes or groups attached"""
        self.client.force_authenticate(user=self.user_author)

        data = {"title": "Best Project Idea"}
        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], data["title"])

    ## DELETE

    def test_delete_project_idea_as_author(self):
        """Verifies that the author of a project idea, that has neither likes nor groups attached, can delete it"""
        self.client.force_authenticate(user=self.user_author)

        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    ### INVALID
    ## PATCH
    def test_update_a_non_existing_project_idea(self):
        """Test that an author can edit their project idea before it has likes or groups attached"""
        self.client.force_authenticate(user=self.user_author)

        url_non_existing_idea = reverse('projects:project-idea-detail', kwargs={'idea_pk': 999999})
        data = {"title": "Non Existing Project Idea"}
        response = self.client.patch(url_non_existing_idea, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIs(response.data.get("title"), None)

    def test_update_a_single_project_idea_as_guest(self):
        """Test that an author can edit their project idea before it has likes or groups attached"""
        self.client.logout()

        data = {"title": "Not My Project Idea"}
        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIs(response.data.get("title"), None)

    def test_update_a_single_project_idea_as_other_user(self):
        """Test that an author can edit their project idea before it has likes or groups attached"""
        self.client.force_authenticate(user=self.user_other)

        data = {"title": "Not My Project Idea"}
        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIs(response.data.get("title"), None)

    ## DELETE
    def test_delete_project_idea_as_guest(self):
        """Ensures that a a guest cannot update a project idea's content"""
        self.client.logout()

        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_idea_as_other_user(self):
        """Ensures that another user that is not the author of a project idea cannot delete it"""
        self.client.force_authenticate(user=self.user_other)

        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    ## SERIALIZER CONNECTION
    def test_update_project_idea_with_profane_content(self):
        """Makes sure that the view rejects banned words correctly (via serializer)"""
        self.client.force_authenticate(user=self.user_author)
        data = {"title": "Fuck this!"}

        response = self.client.patch(self.url_detail, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
