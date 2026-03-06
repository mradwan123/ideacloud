from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models import ProjectGroup, ProjectIdea
from ..serializers.serializer_project_group_serializer import ProjectGroupSerializer
from django.db import transaction


class ProjectGroupList(APIView):
    """
    List all project groups for a specific project idea, or create a new project group.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, idea_pk):
        """
        Retrieve all project groups belonging to a specific project idea.
        """
        try:
            ProjectIdea.objects.get(id=idea_pk)
        except ProjectIdea.DoesNotExist:
            return Response({"error": f"ProjectIdea with ID '{idea_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        queryset = ProjectGroup.objects.filter(project_idea__id=idea_pk)

        serializer = ProjectGroupSerializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, idea_pk):
        """
        Create a new project group for a specific project idea.
        """
        try:
            project_idea = ProjectIdea.objects.get(id=idea_pk)
        except ProjectIdea.DoesNotExist:
            return Response({"error": f"ProjectIdea with ID '{idea_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        context = {"request": request,
                   "project_idea": project_idea}
        serializer = ProjectGroupSerializer(data=request.data, context=context)

        serializer.is_valid(raise_exception=True)

        group = serializer.save()

        return Response({"detail": f"The project group '{group.name}' has been created with ID {group.id}."},
                        status=status.HTTP_201_CREATED)

class ProjectGroupDetail(APIView):
    """
    Retrieve, update, or delete a specific project group within a project idea.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def _get_project_group(self, group_pk):
        try:
            project_group = ProjectGroup.objects.get(id=group_pk)
        except ProjectGroup.DoesNotExist:
            return None

        return project_group

    def _is_project_group_attached_to_project_idea(self, project_group, idea_pk):
        return project_group.project_idea.id == idea_pk

    def get(self, request, idea_pk, group_pk):
        """
        Retrieve details of a specific project group.
        """
        group = self._get_project_group(group_pk)

        if not group:
            return Response({"error": f"ProjectGroup with ID '{group_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if not self._is_project_group_attached_to_project_idea(group, idea_pk):
            return Response({"error": f"ProjectGroup with ID '{group_pk}' not found under ProjectIdea with ID '{idea_pk}'."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectGroupSerializer(group)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, idea_pk, group_pk):
        """
        Fully update a specific project group.
        """
        group = self._get_project_group(group_pk)

        if not group:
            return Response({"error": f"ProjectGroup with ID '{group_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if not self._is_project_group_attached_to_project_idea(group, idea_pk):
            return Response({"error": f"ProjectGroup with ID '{group_pk}' not found under ProjectIdea with ID '{idea_pk}'."},
                            status=status.HTTP_404_NOT_FOUND)

        context = {"request": request,
                   "project_idea": group.project_idea}

        serializer = ProjectGroupSerializer(group, data=request.data, context=context, partial=False)

        serializer.is_valid(raise_exception=True)

        group = serializer.save()

        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def patch(self, request, idea_pk, group_pk):
        """
        Partially update a specific project group.
        """
        group = self._get_project_group(group_pk)

        if not group:
            return Response({"error": f"ProjectGroup with ID '{group_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if not self._is_project_group_attached_to_project_idea(group, idea_pk):
            return Response({"error": f"ProjectGroup with ID '{group_pk}' not found under ProjectIdea with ID '{idea_pk}'."},
                            status=status.HTTP_404_NOT_FOUND)

        context = {"request": request,
                   "project_idea": group.project_idea}

        serializer = ProjectGroupSerializer(group, data=request.data, context=context, partial=True)

        serializer.is_valid(raise_exception=True)

        group = serializer.save()

        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def delete(self, request, idea_pk, group_pk):
        """
        Delete a specific project group.
        """
        group = self._get_project_group(group_pk)

        if not group:
            return Response({"error": f"ProjectGroup with ID '{group_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if not self._is_project_group_attached_to_project_idea(group, idea_pk):
            return Response({"error": f"ProjectGroup with ID '{group_pk}' not found under ProjectIdea with ID '{idea_pk}'."},
                            status=status.HTTP_404_NOT_FOUND)

        group_name = group.name

        group.delete()

        return Response({"detail": f"The project group '{group_name}' has been deleted."},
                        status=status.HTTP_200_OK)


class ProjectGroupMembershipToggle(APIView):
    """
    /project-ideas/<idea_pk>/project-groups/<int:group_pk>/join-leave/
    Methods:
        POST:   Toggles the membership status for the authenticated user.
                Moves ownership to another user if the owner leaves.
                Deletes group if last member leaves
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, idea_pk, group_pk):
        # verify group belongs to idea
        group = get_object_or_404(ProjectGroup, id=group_pk, project_idea=idea_pk)
        user = request.user

        # deny changes to the membership if the group has a finished project attached
        if group.groups_finished_projects.exists():
            return Response({"error": "Membership locked, because the project is finished."}, status=status.HTTP_403_FORBIDDEN)
        # if anything crashes during the owner swap, the user is not removed from the members list
        with transaction.atomic():
            # check if the user is actually in the group
            is_member = group.members.filter(id=user.id).exists()
            if is_member:
                # leave the group
                group.members.remove(user)
                has_joined = False
                # if the leaving member is the owner, transfer ownership
                if group.owner == user:
                    next_owner = group.members.all().first()
                    # if there is still someone left in the group, appoint them as the new owner
                    if next_owner:
                        group.owner = next_owner
                        group.save()
                    else:
                        # if the last member leaves, delete the group
                        group.delete()
                        return Response(
                            {"detail": "You left the group. It has been deleted because it is now empty."},
                            status=status.HTTP_204_NO_CONTENT
                        )

            # if the user is not a member, add them to the group
            else:
                group.members.add(user)
                has_joined = True

        # group data is not too big, so we can return the whole thing here
        serializer = ProjectGroupSerializer(group)
        data = serializer.data
        # add our custom fields for the frontend
        data["action"] = "joined" if has_joined else "left"

        return Response(data, status=status.HTTP_200_OK)
