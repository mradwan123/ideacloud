from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from projects.models import ProjectIdea, ProjectGroup, FinishedProject, Tag

User = get_user_model()

class ProjectIdeaLikesTest(APITestCase):
    def setUp(self):
        # create users
        self.user_author = User.objects.create_user(username="author", password="password", email="author@email.com")
        self.user_other = User.objects.create_user(username="other", password="password", email="other@email.com")
        # create project idea
        self.project_idea = ProjectIdea.objects.create(
            title="Project Idea",
            description="Testing Like Views",
            author=self.user_author
        )
        # helper to manage urls easier
        self.url_idea = reverse("projects:project-idea-like", kwargs={"idea_pk": self.project_idea.pk})

    ### VALID
    ## POST
    def test_project_idea_toggle_like_unliked_authenticated_user(self):
        """Verify that liking a idea as an authenticated user adds them to the likes and returns the right values"""
        self.client.force_authenticate(user=self.user_author)
        response = self.client.post(self.url_idea)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("likes_count"), 1)
        self.assertTrue(response.data.get("has_liked"))
        self.assertTrue(self.project_idea.likes.filter(id=self.user_author.id).exists())

    def test_project_idea_toggle_like_unliked_additional_authenticated_user(self):
        """Verify that liking a idea that already has a like works as intended"""
        self.client.force_authenticate(user=self.user_other)
        # pre-like the idea as author so it is already liked for the test
        self.project_idea.likes.add(self.user_author)

        response = self.client.post(self.url_idea)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("likes_count"), 2)
        self.assertTrue(response.data.get("has_liked"))
        self.assertTrue(self.project_idea.likes.filter(id=self.user_author.id).exists())
        self.assertTrue(self.project_idea.likes.filter(id=self.user_other.id).exists())

    def test_project_idea_toggle_like_liked_authenticated_user(self):
        """Verify that liking an already liked idea as an authenticated user removes them from the likes and returns the right values"""
        self.client.force_authenticate(user=self.user_author)
        # pre-like the idea so it is already liked for the test
        self.project_idea.likes.add(self.user_author)

        response = self.client.post(self.url_idea)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("likes_count"), 0)
        self.assertFalse(response.data.get("has_liked"))
        self.assertFalse(self.project_idea.likes.filter(id=self.user_author.id).exists())

    ### INVALID
    ## POST
    def test_project_idea_toggle_like_unliked_guest(self):
        """Verify that liking a idea as a guest doesn't work"""
        self.client.logout()
        response = self.client.post(self.url_idea)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.project_idea.likes.count(), 0)

    def test_project_idea_toggle_like_liked_guest(self):
        """Verify that unliking a idea as a guest doesn't work"""
        self.client.logout()
        # pre-like the idea so it is already liked for the test
        self.project_idea.likes.add(self.user_author)

        response = self.client.post(self.url_idea)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.project_idea.likes.count(), 1)

    def test_project_idea_toggle_like_nonexistent(self):
        """Verify that liking a idea that doesn't exist, doesn't work"""
        self.client.force_authenticate(user=self.user_other)

        self.url_idea = reverse("projects:project-idea-like", kwargs={"idea_pk": 999999})
        response = self.client.post(self.url_idea)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class FinishedProjectLikesTest(APITestCase):
    def setUp(self):
        # create users
        self.user_author = User.objects.create_user(username="author", password="password", email="author@email.com")
        self.user_other = User.objects.create_user(username="other", password="password", email="other@email.com")
        # create project idea
        self.project_idea = ProjectIdea.objects.create(
            title="Project Idea",
            description="Testing Like Views",
            author=self.user_author
        )
        # create project group
        self.project_group = ProjectGroup.objects.create(
            name="Test Group",
            description="Testing Like Views",
            project_idea=self.project_idea,
            owner=self.user_author
        )
        # create finished project
        self.finished_project = FinishedProject.objects.create(
            title="Finished Project",
            description="Testing Like Views",
            project_group=self.project_group
        )
        # helper to manage urls easier
        self.url_finished = reverse("projects:finished-project-like", kwargs={"project_pk": self.finished_project.pk})

    ### VALID
    ## POST
    def test_finished_project_toggle_like_unliked_authenticated_user(self):
        """Verify that liking a finished project as an authenticated user adds them to the likes and returns the right values"""
        self.client.force_authenticate(user=self.user_author)
        response = self.client.post(self.url_finished)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("likes_count"), 1)
        self.assertTrue(response.data.get("has_liked"))
        self.assertTrue(self.finished_project.likes.filter(id=self.user_author.id).exists())

    def test_finished_project_toggle_like_unliked_additional_authenticated_user(self):
        """Verify that liking a finished project that already has a like works as intended"""
        self.client.force_authenticate(user=self.user_other)
        # pre-like the idea as author so it is already liked for the test
        self.finished_project.likes.add(self.user_author)

        response = self.client.post(self.url_finished)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("likes_count"), 2)
        self.assertTrue(response.data.get("has_liked"))
        self.assertTrue(self.finished_project.likes.filter(id=self.user_author.id).exists())
        self.assertTrue(self.finished_project.likes.filter(id=self.user_other.id).exists())

    def test_finished_project_toggle_like_liked_authenticated_user(self):
        """Verify that liking an already liked finished project as an authenticated user removes them from the likes and returns the right values"""
        self.client.force_authenticate(user=self.user_author)
        # pre-like the finished project so it is already liked for the test
        self.finished_project.likes.add(self.user_author)

        response = self.client.post(self.url_finished)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("likes_count"), 0)
        self.assertFalse(response.data.get("has_liked"))
        self.assertFalse(self.finished_project.likes.filter(id=self.user_author.id).exists())

    ### INVALID
    ## POST
    def test_finished_project_toggle_like_unliked_guest(self):
        """Verify that liking a finished project as a guest doesn't work"""
        self.client.logout()
        response = self.client.post(self.url_finished)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.finished_project.likes.count(), 0)

    def test_finished_project_toggle_like_liked_guest(self):
        """Verify that unliking a finished project as a guest doesn't work"""
        self.client.logout()
        # pre-like the finished project so it is already liked for the test
        self.finished_project.likes.add(self.user_author)

        response = self.client.post(self.url_finished)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.finished_project.likes.count(), 1)

    def test_finished_project_toggle_like_nonexistent(self):
        """Verify that liking a finished project that doesn't exist, doesn't work"""
        self.client.force_authenticate(user=self.user_other)

        self.url_finished = reverse("projects:finished-project-like", kwargs={"project_pk": 999999})
        response = self.client.post(self.url_finished)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
