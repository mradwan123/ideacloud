from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from projects.models import ProjectIdea, ProjectGroup
from projects.serializers.serializer_project_idea_serializer import ProjectIdeaSerializer


class ProjectIdeaList(APIView):
    """
    /project-ideas/
    Methods:
        GET:  list all ideas with sorting and multi-tag filtering
        POST: create a new idea (authenticated users only)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        Return a list of all ideas with optional  filtering
        query_params:   sort - how the return data should be sorted (e.g., ?sort=title or ?sort=-created_on); "-" makes it descending
                        tag  - filter for multiple tags (e.g., ?tags=python,django)
        """
        # sort like specified in the 'sort' instruction from the URL (e.g. /project-ideas/?sort=title); default to '-created_on'
        sort_by = request.query_params.get('sort', '-created_on')

        # .getlist() gets multiple values like ?tag=python&tag=automation
        tags = request.query_params.getlist('tag')

        # get all project ideas from the db and sort the data as dictated by sort_by
        queryset = ProjectIdea.objects.all().order_by(sort_by)
        if tags:
            # get all project ideas from the db that match certain tags
            # .distinct() ensures we don't get the same project twice if it matches multiple tags
            # tags__name__in: tags    : looks in the tags field of the ProjectIdea model
            #               __name    : checks the name field of the Tag model (through the relationship)
            #                 __in    : field lookup; checks if the name is found anywhere inside the tags list we provide
            queryset = queryset.filter(tags__name__in=tags).distinct()

        # serialization (object -> json)
        serializer = ProjectIdeaSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new ProjectIdea with the provided data and authenticated user"""
        serializer = ProjectIdeaSerializer(data=request.data)

        # validation check for model requirements
        # if validation fails DRF stops here and sends a 400 Bad Request back to the user (so we don't have to use any if logic)
        serializer.is_valid(raise_exception=True)

        # the json doesn't include the autor, so we 'inject' the logged-in user here
        # this ensures the post is linked to the right person safely and automatically
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProjectIdeaDetail(APIView):
    """
    /project-ideas/<project_idea_id>/
    Methods:
        GET:    get a specific idea
        PATCH:  partial update  (author only and only if no groups/likes are connected)
        DELETE: remove idea     (author only and only if no groups/likes are connected)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def _get_object(self, pk):
        """Helper to find the project idea or return 404"""
        # we could do this in each method but having it centralized here makes easier changes in the long run
        return get_object_or_404(ProjectIdea, pk=pk)

    def _is_protected(self, instance):
        """
        Check if the idea has connected groups or likes and flag itself as protected in the return, if that's the case
        related_names: 'project_group_project_idea' and 'likes'
        """
        # .exists() is an efficient way to check for relationships without loading all data
        return instance.project_group_project_idea.exists() or instance.likes.exists()

    def get(self, request, pk):
        """Return a single project idea via its id"""
        project_idea = self._get_object(pk)
        serializer = ProjectIdeaSerializer(project_idea)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        """Update certain fields of the project idea"""
        project_idea = self._get_object(pk)

        if request.user != project_idea.author:
            return Response(
                {"detail": "Only the author is allowed to edit the project idea"},
                status=status.HTTP_403_FORBIDDEN
            )

        if self._is_protected(project_idea):
            return Response(
                {"detail": "This project idea has likes or groups connected and therefore can't be edited."},
                status=status.HTTP_409_CONFLICT
            )

        # partial=True allows missing fields in the request and is therefore essential for the patch logic
        serializer = ProjectIdeaSerializer(project_idea, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete a single project idea via its id"""
        project_idea = self._get_object(pk)

        if request.user != project_idea.author:
            return Response(
                {"detail": "Only the author is allowed to delete the project idea"},
                status=status.HTTP_403_FORBIDDEN
            )

        if self._is_protected(project_idea):
            return Response(
                {"detail": "This project idea has likes or groups connected and therefore can't be deleted."},
                status=status.HTTP_409_CONFLICT
            )

        project_idea.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
