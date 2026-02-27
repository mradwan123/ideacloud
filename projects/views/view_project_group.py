from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models import ProjectGroup, ProjectIdea
from ..serializers.serializer_project_group_serializer import ProjectGroupSerializer

class ProjectGroupList(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, idea_pk):
        try:
            ProjectIdea.objects.get(id=idea_pk)
        except ProjectIdea.DoesNotExist:
            return Response({"error": f"ProjectIdea with ID '{idea_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)
        
        queryset = ProjectGroup.objects.filter(project_idea__id=idea_pk)

        serializer = ProjectGroupSerializer(queryset, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, idea_pk):
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

        return Response({"detail": f"The project group '{group.name}' has been updated."},
                        status=status.HTTP_200_OK)

    def patch(self, request, idea_pk, group_pk):
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

        return Response({"detail": f"The project group '{group.name}' has been updated."},
                        status=status.HTTP_200_OK)

    def delete(self, request, idea_pk, group_pk):
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
