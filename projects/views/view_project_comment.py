from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from datetime import timedelta
from ..models import ProjectIdea, FinishedProject, ProjectComment
from projects.serializers.serializer_project_comment import ProjectCommentSerializer


# technically belongs in the permissions file but because we didn't use them really and this here is specific, I keep it here
class IsAuthorAndWithinTimeframe(permissions.BasePermission):
    """Allows non-safe methods (delete, put, patch, post) only if the user is the author and less than 15 minutes have passed since comment creation."""
    def has_object_permission(self, request, view, obj):
        # read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # check for ownership
        if obj.author != request.user:
            self.message = "Only the author of this comment can modify it."
            return False

        expiration_time = timedelta(minutes=15)
        is_in_time = timezone.now() <= (obj.created_on + expiration_time)
        # we compare the time now (eg. 14:20) with the creation time + our limit (eg 14:00 + 15 min)
        if not is_in_time:
            self.message = f"Comment is too old now. Editing after {expiration_time} minutes is prohibited."
            return False

        return True


class ProjectIdeaCommentList(APIView):
    """
    /project-ideas/<idea_pk>/project-comments/
    Methods:
        GET:  list all comments attached to a specific idea
        POST: create a new comment (authenticated users only)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, idea_pk):
        """Lists all comments for a specifc idea"""
        # check if the idea object exists. We don't need it further
        get_object_or_404(ProjectIdea, pk=idea_pk)

        queryset = ProjectComment.objects.filter(project_idea_id=idea_pk).order_by("-created_on")
        serializer = ProjectCommentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, idea_pk):
        """Create a comment linked to a specific idea (from the url)"""
        project_idea = get_object_or_404(ProjectIdea, pk=idea_pk)

        serializer = ProjectCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # we manually inject the author and project_idea
        serializer.save(author=request.user, project_idea=project_idea)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectIdeaCommentDetail(APIView):
    """
    /project-ideas/<idea_pk>/project-comments/<comment_pk>
    Methods:
        GET:    get a specific comment
        PATCH:  partial update (only as author and before our set time-limit is reached)
        DELETE: remove comment (only as author and before our set time-limit is reached)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorAndWithinTimeframe]

    def get(self, request, idea_pk, comment_pk):
        """Gets a specific comment for a specifc idea"""
        # check if the idea object exists. We don't need it further
        comment = get_object_or_404(ProjectComment, pk=comment_pk, project_idea_id=idea_pk)

        serializer = ProjectCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, idea_pk, comment_pk):
        """Update the content of a comment up to the set time-limit after creation"""
        comment = get_object_or_404(ProjectComment, pk=comment_pk, project_idea_id=idea_pk)

        # this triggers the permission_classes checks
        self.check_object_permissions(request, comment)

        serializer = ProjectCommentSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, idea_pk, comment_pk):
        """Delete the comment up to the set time-limit after creation"""
        comment = get_object_or_404(ProjectComment, pk=comment_pk, project_idea_id=idea_pk)

        self.check_object_permissions(request, comment)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FinishedProjectCommentList(APIView):
    """
    /finished-projects/<finished_pk>/project-comments/
    Methods:
        GET:  list all comments attached to a specific finished project
        POST: create a new comment (authenticated users only)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, finished_pk):
        """Lists all comments for a specifc finished project"""
        # check if the project object exists. We don't need it further
        get_object_or_404(FinishedProject, pk=finished_pk)

        queryset = ProjectComment.objects.filter(finished_project_id=finished_pk).order_by("-created_on")
        serializer = ProjectCommentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, finished_pk):
        """Create a comment linked to a specific finished project (from the url)"""
        finished_project = get_object_or_404(FinishedProject, pk=finished_pk)

        serializer = ProjectCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # we manually inject the author and finished_project
        serializer.save(author=request.user, finished_project=finished_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FinishedProjectCommentDetail(APIView):
    """
    /finished-project/<finished_pk>/project-comments/<comment_pk>
    Methods:
        GET:    get a specific comment
        PATCH:  partial update (only as author and before our set time-limit is reached)
        DELETE: remove comment (only as author and before our set time-limit is reached)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorAndWithinTimeframe]

    def get(self, request, finished_pk, comment_pk):
        """Gets a specific comment for a specifc finished project"""
        # check if the finished project object exists. We don't need it further
        comment = get_object_or_404(ProjectComment, pk=comment_pk, finished_project_id=finished_pk)

        serializer = ProjectCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, finished_pk, comment_pk):
        """Update the content of a comment up to the set time-limit after creation"""
        comment = get_object_or_404(ProjectComment, pk=comment_pk, finished_project_id=finished_pk)

        # this triggers the permission_classes checks
        self.check_object_permissions(request, comment)

        serializer = ProjectCommentSerializer(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, finished_pk, comment_pk):
        """Delete the comment up to the set time-limit after creation"""
        comment = get_object_or_404(ProjectComment, pk=comment_pk, finished_project_id=finished_pk)

        self.check_object_permissions(request, comment)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
