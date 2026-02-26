from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models import ProjectGroup
from ..serializers.serializer_project_group_serializer import ProjectGroupSerializer

class ProjectGroupList(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, project_idea_id):
        queryset = ProjectGroup.objects.filter(id=project_idea_id)

        serializer = ProjectGroupSerializer(queryset)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_idea_id):
        data = request.data
        data["project_idea"] = project_idea_id
        data["owner"] = request.user.id
        serializer = ProjectGroupSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        group = serializer.save()

        return Response({"detail": f"The project group '{group.name}' has been created with ID {group.id}."},
                        status=status.HTTP_201_CREATED)


class ProjectGroupDetails(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def _get_project_group(self, project_idea_id, project_group_id):
        try:
            group = ProjectGroup.objects.get(id=project_group_id)
        except:
            return None
        
        if group.project_idea.id != project_idea_id:
            return None
        
        return group

    def get(self, request, project_idea_id, project_group_id):
        group = self._get_project_group(project_idea_id, project_group_id)

        if not group:
            return Response({"error": "Project group not found."},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProjectGroupSerializer(group)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def put(self, request, project_idea_id, project_group_id):
        group = self._get_project_group(project_idea_id, project_group_id)

        if not group:
            return Response({"error": "Project group not found."},
                            status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProjectGroupSerializer(group)
    
    def patch(self, request):
        pass

    def delete(self, request):
        pass
