from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from PIL import Image
from config.image_helper.base64_image_conversion import base64_to_image

from projects.models import ImageProject, ProjectIdea
from projects.serializers.serializer_image_project import ImageProjectSerializer
import io

class AddProjectIdeaImage(APIView):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, idea_pk):
        """Add image to a given project idea. Can on be done by project idea author.
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
        
        # base64_image = request.data.get("image")
        # if base64_image:
        #     data = {"project_idea": idea_pk,
        #             "image": base64_image}
        # else:
        #     data = None

        request.data["project_idea"] = idea_pk
            
        serializer = ImageProjectSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()
        
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

class RemoveProjectIdeaImage(APIView):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, idea_pk):
        """Remove an image from a given project idea by id. Can on be done by project idea author.
        Data:
        {
            "image_id": [id of image you want to remove]
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

        image_id = request.data.get("image_id")
        if not image_id:
            return Response({"error": "No image_id given."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            image = ImageProject.objects.get(id=image_id)
        except ImageProject.DoesNotExist:
            return Response({"error": f"Image with ID '{image_id}' not found under project idea '{idea_pk}'."},
                            status=status.HTTP_404_NOT_FOUND)
        
        if image.project_idea.id != idea_pk:
            return Response({"error": f"Image with ID '{image_id}' not found under project idea '{idea_pk}'."},
                            status=status.HTTP_404_NOT_FOUND)
        
        image.delete()

        return Response({"detail": f"Image with ID '{image_id}' has been delete from project idea '{idea_pk}'."},
                        status=status.HTTP_200_OK)
