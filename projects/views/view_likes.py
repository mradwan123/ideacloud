from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from projects.models import ProjectIdea, FinishedProject

# we don't use any get logic for likes because the appropriate values are already included in the
# respective views of ProjectIdea and FinishedProject. Same goes for the URLs


class ProjectIdeaToggleLike(APIView):
    """
    /project-ideas/<idea_pk>/lik/
    Methods:
        POST: Toggles the like status for the authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]

    # we're using ONLY a post request to toggle the like. Using a delete would make us have to check if its already liked
    # on the frontend, which would introduce new problems if eg. the user has multiple tabs open
    def post(self, request, idea_pk):
        project_idea = get_object_or_404(ProjectIdea, pk=idea_pk)
        user = request.user

        if project_idea.likes.filter(id=user.id).exists():
            project_idea.likes.remove(user)
            has_liked = False
        else:
            project_idea.likes.add(user)
            has_liked = True

        # returning the count and the status allows the frontend to update the UI without issuing a new GET request
        return Response(
            {
                "likes_count": project_idea.likes.count(),
                "has_liked": has_liked
            },
            status=status.HTTP_200_OK
        )


class FinishedProjectToggleLike(APIView):
    """
    /finished-projects/<project_pk>/like/
    Methods:
        POST: Toggles the like status for the authenticated user
    """
    permission_classes = [permissions.IsAuthenticated]

    # we're using ONLY a post request to toggle the like. Using a delete would make us have to check if its already liked
    # on the frontend, which would introduce new problems if eg. the user has multiple tabs open
    def post(self, request, project_pk):
        finished_project = get_object_or_404(FinishedProject, pk=project_pk)
        user = request.user

        if finished_project.likes.filter(id=user.id).exists():
            finished_project.likes.remove(user)
            has_liked = False
        else:
            finished_project.likes.add(user)
            has_liked = True

        # returning the count and the status allows the frontend to update the UI without issuing a new GET request
        return Response(
            {
                "likes_count": finished_project.likes.count(),
                "has_liked": has_liked
            },
            status=status.HTTP_200_OK
        )
