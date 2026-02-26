from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models import ProjectGroup, ProjectIdea
from ..serializers.serializer_project_group_serializer import ProjectGroupSerializer

class ProjectGroupList(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, project_idea_id):
        queryset = ProjectGroup.objects.filter(project_idea__id=project_idea_id)

        serializer = ProjectGroupSerializer(queryset)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, project_idea_id):
        try:
            project_idea = ProjectIdea.objects.get(id=project_idea_id)
        except ProjectIdea.DoesNotExist:
            return Response({"error": f"ProjectIdea with ID '{project_idea_id}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)
        
        context = {"request": request,
                   "project_idea": project_idea}
        serializer = ProjectGroupSerializer(data=request.data, context=context)

        serializer.is_valid(raise_exception=True)

        group = serializer.save()

        return Response({"detail": f"The project group '{group.name}' has been created with ID {group.id}."},
                        status=status.HTTP_201_CREATED)


class ProjectGroupDetails(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def _get_project_group(self, project_group_id):
        try:
            project_group = ProjectGroup.objects.get(id=project_group_id)
        except ProjectGroup.DoesNotExist:
            return None
        
        return project_group
    
    def _is_project_group_attached_to_project_idea(self, project_group, project_idea_id):
        return project_group.project_idea.id == project_idea_id

    def get(self, request, project_idea_id, project_group_id):
        group = self._get_project_group(project_group_id)

        if not group:
            return Response({"error": f"ProjectGroup with ID '{project_group_id}' does not exist."},
                     status=status.HTTP_404_NOT_FOUND)
            
        if not self._is_project_group_attached_to_project_idea(group, project_idea_id)
            return Response({"error": f"ProjectGroup with ID '{project_group_id}' not found under ProjectIdea with ID '{project_idea_id}'."},
                     status=status.HTTP_404_NOT_FOUND)
            
        serializer = ProjectGroupSerializer(group)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def put(self, request, project_idea_id, project_group_id):
        group = self._get_project_group(project_group_id)

        if not group:
            return Response({"error": f"ProjectGroup with ID '{project_group_id}' does not exist."},
                     status=status.HTTP_404_NOT_FOUND)
            
        if not self._is_project_group_attached_to_project_idea(group, project_idea_id)
            return Response({"error": f"ProjectGroup with ID '{project_group_id}' not found under ProjectIdea with ID '{project_idea_id}'."},
                     status=status.HTTP_404_NOT_FOUND)
        
        context = {"request": request,
                   "project_idea": group.project_idea}
        
        serializer = ProjectGroupSerializer(group, data=request.data, context=context, partial=False)

        serializer.is_valid(raise_exception=True)

        group = serializer.save()

        return Response({"detail": f"The project group '{group.name}' has been updated."},
                        status=status.HTTP_200_OK)

    
    def patch(self, request, project_idea_id, project_group_id):
        group = self._get_project_group(project_group_id)

        if not group:
            return Response({"error": f"ProjectGroup with ID '{project_group_id}' does not exist."},
                     status=status.HTTP_404_NOT_FOUND)
            
        if not self._is_project_group_attached_to_project_idea(group, project_idea_id)
            return Response({"error": f"ProjectGroup with ID '{project_group_id}' not found under ProjectIdea with ID '{project_idea_id}'."},
                     status=status.HTTP_404_NOT_FOUND)
        
        context = {"request": request,
                   "project_idea": group.project_idea}
        
        serializer = ProjectGroupSerializer(group, data=request.data, context=context, partial=True)

        serializer.is_valid(raise_exception=True)

        group = serializer.save()

        return Response({"detail": f"The project group '{group.name}' has been updated."},
                        status=status.HTTP_200_OK)

    def delete(self, request, project_idea_id, project_group_id):
        group = self._get_project_group(project_group_id)

        if not group:
            return Response({"error": f"ProjectGroup with ID '{project_group_id}' does not exist."},
                     status=status.HTTP_404_NOT_FOUND)
            
        if not self._is_project_group_attached_to_project_idea(group, project_idea_id)
            return Response({"error": f"ProjectGroup with ID '{project_group_id}' not found under ProjectIdea with ID '{project_idea_id}'."},
                     status=status.HTTP_404_NOT_FOUND)
        
        group_name = group.name
        
        group.delete()

        return Response({"detail": f"The project group '{group_name}' has been deleted."},
                        status=status.HTTP_200_OK)
