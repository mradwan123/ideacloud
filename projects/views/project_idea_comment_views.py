from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models import ProjectIdeaComment
from ..serializers import serializer_project_idea_comment



class ProjectIdeaCommentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        comments = ProjectIdeaComment.objects.filter(project_idea_id=project_id)
        serializer = serializer_project_idea_comment(comments, many=True)
        return Response(serializer.data)

    def post(self, request, project_id):
        serializer = serializer_project_idea_comment(data=request.data)
        if serializer.is_valid():
            serializer.save(
            user=request.user,
            project_idea_id=project_id
            )
            return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)