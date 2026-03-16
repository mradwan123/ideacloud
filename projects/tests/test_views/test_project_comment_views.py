from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from projects.models import ProjectIdea, FinishedProject, ProjectComment, ProjectGroup

User = get_user_model()

class ProjectIdeaCommentListTests(APITestCase):
    def setUp(self):
        self.user_author = User.objects.create_user(username="author", password="password", email="author@email.com")
        self.user_other = User.objects.create_user(username="other", password="password", email="other@email.com")

        self.project_idea = ProjectIdea.objects.create(
            title="Test Idea",
            description="Idea Description",
            author=self.user_author
        )

        self.comment = ProjectComment.objects.create(
            content="Original Comment",
            author=self.user_author,
            project_idea=self.project_idea
        )

        self.url_list = reverse("projects:project-idea-comments-list", kwargs={"idea_pk": self.project_idea.pk})

    ### VALID
    ## GET
    def test_list_comments_guest(self):
        """Verify anyone can see the comments to an idea"""
        self.client.logout()

        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # just checking for anything if it really matches our test comment
        self.assertEqual(response.data[0]["author"], self.user_author.username)

    ## POST
    def test_create_comment_authenticated(self):
        """Verify an authenticatet user can create a new comment on an idea"""
        self.client.force_authenticate(user=self.user_other)

        data = {"content": "Cool idea!"}
        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProjectComment.objects.count(), 2)
        self.assertEqual(response.data["author"], self.user_other.username)

    ### INVALID
    ## POST
    def test_create_comment_guest(self):
        """Verify a guest user cannot create a new comment on an idea"""
        self.client.logout()

        data = {"content": "Cool idea!"}
        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProjectIdeaCommentDetailTests(APITestCase):
    def setUp(self):
        self.user_author = User.objects.create_user(username="author", password="password", email="author@email.com")
        self.user_other = User.objects.create_user(username="other", password="password", email="other@email.com")

        self.project_idea = ProjectIdea.objects.create(
            title="Test Idea",
            description="Idea Description",
            author=self.user_author
        )

        self.comment = ProjectComment.objects.create(
            content="Original Comment",
            author=self.user_author,
            project_idea=self.project_idea
        )

        self.url_detail = reverse("projects:project-idea-comments-detail", kwargs={"idea_pk": self.project_idea.pk, "comment_pk": self.comment.pk})

    ### VALID
    ## GET
    def test_get_comment_detail(self):
        """Verify anyone can retrieve a specific comment"""
        self.client.logout()

        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Original Comment")

    ## PATCH
    def test_update_comment_as_author_within_timeframe(self):
        """Verify the author can update their comment within the set timeframe"""
        self.client.force_authenticate(user=self.user_author)
        data = {"content": "Updated Idea Comment"}

        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Updated Idea Comment")

    ## DELETE
    def test_delete_comment_as_author(self):
        """Verify the author can delete their comment within the set timeframe"""
        self.client.force_authenticate(user=self.user_author)

        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProjectComment.objects.count(), 0)

    ### INVALID
    ## PATCH
    def test_update_comment_as_guest(self):
        """Verify guests cannot update a comment"""
        self.client.logout()

        data = {"content": "Modified Comment"}
        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_as_other_user(self):
        """Verify non-authors cannot update someone else's comment"""
        self.client.force_authenticate(user=self.user_other)

        data = {"content": "Modified Comment"}
        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_comment_after_timeframe(self):
        """Verify the author cannot update their comment after 15 minutes"""
        expired_time = timezone.now() - timedelta(minutes=16)
        # manually modifying the creation time here
        ProjectComment.objects.filter(pk=self.comment.pk).update(created_on=expired_time)

        self.client.force_authenticate(user=self.user_author)
        data = {"content": "Trying to update too late"}

        response = self.client.patch(self.url_detail, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # DELETE
    def test_delete_comment_as_guest(self):
        """Verify the author can delete their comment within 15 minutes"""
        self.client.logout()
        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ProjectComment.objects.count(), 1)

    def test_delete_comment_as_other_user(self):
        """Verify a user that is not the author cannot delete a comment"""
        self.client.force_authenticate(user=self.user_other)
        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ProjectComment.objects.count(), 1)


class FinishedProjectCommentListTests(APITestCase):
    def setUp(self):
        self.user_author = User.objects.create_user(username="author", password="password", email="author@email.com")
        self.user_other = User.objects.create_user(username="other", password="password", email="other@email.com")

        # create an Idea to have something to attach the group to
        self.project_idea = ProjectIdea.objects.create(
            title="Idea for Group",
            description="Base Idea",
            author=self.user_author
        )

        # create the group linked to the Idea
        self.group = ProjectGroup.objects.create(
            name="Test Group",
            owner=self.user_author,
            project_idea=self.project_idea
        )

        self.finished_project = FinishedProject.objects.create(
            title="Finished Test Project",
            description="Project done",
            project_group=self.group
        )

        self.comment = ProjectComment.objects.create(
            content="Original Finished Comment",
            author=self.user_author,
            finished_project=self.finished_project
        )
        self.url_list = reverse("projects:finished-project-comments-list", kwargs={"finished_pk": self.finished_project.pk})

    ### VALID
    ## GET
    def test_list_comments_guest(self):
        """Verify anyone can see the comments on a finished project"""
        self.client.logout()

        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["author"], self.user_author.username)

    ## POST
    def test_create_comment_authenticated(self):
        """Verify an authenticated user can create a new comment on a finished project"""
        self.client.force_authenticate(user=self.user_other)

        data = {"content": "Looks good!"}
        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProjectComment.objects.count(), 2)
        self.assertEqual(response.data["author"], self.user_other.username)

    ### INVALID
    ## POST
    def test_create_comment_guest(self):
        """Verify a guest user cannot create a new comment on a finished project"""
        self.client.logout()

        data = {"content": "Great work!"}
        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FinishedProjectCommentDetailTests(APITestCase):
    def setUp(self):
        self.user_author = User.objects.create_user(username="author", password="password", email="author@email.com")
        self.user_other = User.objects.create_user(username="other", password="password", email="other@email.com")

        # create an Idea to have something to attach the group to
        self.project_idea = ProjectIdea.objects.create(
            title="Idea for Group",
            description="Base Idea",
            author=self.user_author
        )

        # create the group linked to the Idea
        self.group = ProjectGroup.objects.create(
            name="Test Group",
            owner=self.user_author,
            project_idea=self.project_idea
        )

        self.finished_project = FinishedProject.objects.create(
            title="Finished Test Project",
            description="Project done",
            project_group=self.group
        )

        self.comment = ProjectComment.objects.create(
            content="Original Finished Comment",
            author=self.user_author,
            finished_project=self.finished_project
        )

        self.url_detail = reverse("projects:finished-project-comments-detail", kwargs={"finished_pk": self.finished_project.pk, "comment_pk": self.comment.pk})

    ### VALID
    ## GET
    def test_get_comment_detail(self):
        """Verify anyone can retrieve a specific finished project comment"""
        self.client.logout()

        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "Original Finished Comment")

    ## PATCH
    def test_update_comment_as_author_within_timeframe(self):
        """Verify the author can update their comment within the set timeframe"""
        self.client.force_authenticate(user=self.user_author)
        data = {"content": "Updated Finished Comment"}

        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "Updated Finished Comment")

    ## DELETE
    def test_delete_comment_as_author(self):
        """Verify the author can delete their comment within the set timeframe"""
        self.client.force_authenticate(user=self.user_author)

        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProjectComment.objects.count(), 0)

    ### INVALID
    ## PATCH
    def test_update_comment_as_guest(self):
        """Verify guests cannot update a comment"""
        self.client.logout()

        data = {"content": "Modified Comment"}
        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_comment_as_other_user(self):
        """Verify non-authors cannot update someone else's comment"""
        self.client.force_authenticate(user=self.user_other)

        data = {"content": "Modified Comment"}
        response = self.client.patch(self.url_detail, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_comment_after_timeframe(self):
        """Verify the author cannot update their comment after 15 minutes"""
        expired_time = timezone.now() - timedelta(minutes=16)
        ProjectComment.objects.filter(pk=self.comment.pk).update(created_on=expired_time)

        self.client.force_authenticate(user=self.user_author)
        data = {"content": "Trying to update too late"}

        response = self.client.patch(self.url_detail, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # DELETE
    def test_delete_comment_as_guest(self):
        """Verify a guest user cannot delete a comment"""
        self.client.logout()
        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ProjectComment.objects.count(), 1)

    def test_delete_comment_as_other_user(self):
        """Verify a user that is not the author cannot delete a comment"""
        self.client.force_authenticate(user=self.user_other)
        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ProjectComment.objects.count(), 1)
