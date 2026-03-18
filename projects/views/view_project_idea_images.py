from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from PIL import Image
from config.image_helper.base64_image_conversion import base64_to_image

from projects.models import ImageProject, ProjectIdea
from projects.serializers.serializer_image_project import ImageProjectSerializer

class AddProjectIdeaImage(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, idea_pk):
        """Add image to a given project idea. Can on be done by project idea author.

        The image data has to be send as a jpg image in base64 byte format.

        Data:
        {
            "image": [jpg image as bytes in base64 format]
        }
        """
        try:
            project_idea = ProjectIdea.objects.get(id=idea_pk)
        except ProjectIdea.DoesNotExist:
            return Response({"error": f"ProjectIdea with ID '{idea_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if project_idea.author.id != request.user.id:
            return Response({"error": "User unauthorized. Must be author."},
                            status=status.HTTP_401_UNAUTHORIZED)

        request.data["project_idea"] = idea_pk

        serializer = ImageProjectSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

class RemoveProjectIdeaImage(APIView):

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, idea_pk, image_pk):
        """Remove an image from a given project idea by id. Can on be done by project idea author."""
        try:
            project_idea = ProjectIdea.objects.get(id=idea_pk)
        except ProjectIdea.DoesNotExist:
            return Response({"error": f"ProjectIdea with ID '{idea_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)

        if project_idea.author.id != request.user.id:
            return Response({"error": "User unauthorized. Must be author."},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            image = ImageProject.objects.get(id=image_pk)
        except ImageProject.DoesNotExist:
            return Response({"error": f"Image with ID '{image_pk}' not found under project idea '{idea_pk}'."},
                            status=status.HTTP_404_NOT_FOUND)

        if image.project_idea.id != idea_pk:
            return Response({"error": f"Image with ID '{image_pk}' not found under project idea '{idea_pk}'."},
                            status=status.HTTP_404_NOT_FOUND)

        image.delete()

        return Response({"detail": f"Image with ID '{image_pk}' has been delete from project idea '{idea_pk}'."},
                        status=status.HTTP_200_OK)
