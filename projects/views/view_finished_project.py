from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Value, BooleanField, Count, Exists, OuterRef

from projects.models import ProjectIdea, ProjectGroup, FinishedProject
from projects.serializers.serializer_finished_projects import FinishedProjectSerializer

def _get_queryset_with_like_data(user):
    """
    Returns a queryset of ProjectIdeas with likes_count and has_liked status
    Accepts a 'user' object to determine the has_liked status
    """
    # .annotate() adds a virtual column to our result set
    queryset = FinishedProject.objects.all().annotate(likes_count=Count('likes'))

    if user.is_authenticated:
        # create a subquery that looks for a link between the current project (OuterRef) and the logged-in user
        user_has_liked = FinishedProject.objects.filter(pk=OuterRef('pk'), likes=user)
        # annotate with a boolean. True if the subquery finds a match, False if not
        queryset = queryset.annotate(has_liked=Exists(user_has_liked))
    else:
        # false for guests; if the user isn't logged in, we must still provide the 'has_liked' field so the serializer doesn't crash
        queryset = queryset.annotate(has_liked=Value(False, output_field=BooleanField()))

    return queryset


class FinishedProjectList(APIView):
    """
    /finsihed-project/
    Methods:
        GET:  list all finished project with sorting and multi-tag filtering
        POST: publihs a finsihed project (authenticated users only)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        Return a list of all ideas with optional filtering. Also includes the number of likes on a finished project and if the current user already has liked it.
        query_params:   sort - how the return data should be sorted (e.g., ?sort=title or ?sort=-created_on); "-" makes it descending
                        tag  - filter for multiple tags (e.g., ?tags=python,django)
        """
        # sort like specified in the 'sort' instruction from the URL (e.g. /finished-projects/?sort=title); default to '-created_on'
        sort_by = request.query_params.get('sort', '-created_on')

        # .getlist() gets multiple values like ?tag=python&tag=automation
        tags = request.query_params.getlist('tag')

        queryset = _get_queryset_with_like_data(request.user)

        if tags:
            # get all project ideas from the db that match certain tags
            # .distinct() ensures we don't get the same project twice if it matches multiple tags
            # tags__name__in: tags    : looks in the tags field of the ProjectIdea model
            #               __name    : checks the name field of the Tag model (through the relationship)
            #                 __in    : field lookup; checks if the name is found anywhere inside the tags list we provide
            queryset = queryset.filter(tags__name__in=tags).distinct()

        # order the queryset as dictated by sort_by
        queryset = queryset.order_by(sort_by)

        # serialization (object -> json)
        serializer = FinishedProjectSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new FinishedProject with the provided data and authenticated user"""
        serializer = FinishedProjectSerializer(data=request.data)

        # validation check for model requirements
        # if validation fails DRF stops here and sends a 400 Bad Request back to the user (so we don't have to use any if logic)
        serializer.is_valid(raise_exception=True)

        # the json doesn't include the autor, so we 'inject' the logged-in user here
        # this ensures the post is linked to the right person safely and automatically
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FinishedProjectDetail(APIView):
    """
    /finished-projects/<finished_project_id>/
    Methods:
        GET:    get a specific finished project
        PATCH:  partial update  (author only and only if no groups/likes are connected)
        DELETE: remove finished project  (author only and only if no groups/likes are connected)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def _get_object(self, request, finished_pk):
        """Helper to find the project idea or return 404. On GET method, annotate with like data"""
        # we could do this in each method but having it centralized here makes easier changes in the long run
        if request.method == 'GET':
            # use the helper that includes all the extra likes data
            queryset = _get_queryset_with_like_data(request.user)
        else:
            # simple fetch for PATCH/DELETE
            queryset = FinishedProject.objects.all()

        return get_object_or_404(queryset, pk=finished_pk)

    def _is_protected(self, instance):
        """
        Check if the idea has connected groups or likes and flag itself as protected in the return, if that's the case
        related_names: 'project_group_finished_project' and 'likes'
        """
        # .exists() is an efficient way to check for relationships without loading all data
        return instance.project_group_project_idea.exists() or instance.likes.exists()

    def get(self, request, finished_pk):
        """Return a single project idea via its id"""
        finished_project = self._get_object(request, finished_pk)
        serializer = FinishedProjectSerializer(finished_project)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, finished_pk):
        """Update certain fields of the finished project"""
        finished_project = self._get_object(request, finished_pk)

        if request.user != finished_project.author:
            return Response(
                {"detail": "Only the author is allowed to edit the finished project"},
                status=status.HTTP_403_FORBIDDEN
            )

        if self._is_protected(finished_project):
            return Response(
                {"detail": "This finished project has likes or groups connected and therefore can't be edited."},
                status=status.HTTP_409_CONFLICT
            )

        # partial=True allows missing fields in the request and is therefore essential for the patch logic
        serializer = FinishedProjectSerializer(finished_project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, idea_pk):
        """Delete a single finished project via its id"""
        finished_project = self._get_object(request, idea_pk)

        if request.user != finished_project.author:
            return Response(
                {"detail": "Only the author is allowed to delete the finished project"},
                status=status.HTTP_403_FORBIDDEN
            )

        if self._is_protected(finished_project):
            return Response(
                {"detail": "This finished project has likes or groups connected and therefore can't be deleted."},
                status=status.HTTP_409_CONFLICT
            )

        finished_project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
