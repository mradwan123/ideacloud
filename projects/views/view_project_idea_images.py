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
        try:
            ProjectIdea.objects.get(id=idea_pk)
        except ProjectIdea.DoesNotExist:
            return Response({"error": f"ProjectIdea with ID '{idea_pk}' does not exist."},
                            status=status.HTTP_404_NOT_FOUND)
        
        base64_image = request.data.get("image")
        if base64_image:
            data = {"project_idea": idea_pk,
                    "image": base64_image}
        else:
            data = None
            
        serializer = ImageProjectSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        # try:
        #     temp_img = Image.open(base64_to_image(base64_image), formats=['JPEG'])
        #     temp_img.verify()
        # except:
        #     return Response({"error": "Only jpg format allowed for image files."})

        final_image = serializer.save()
        
        return Response({"url": final_image.image.url},
                        status=status.HTTP_201_CREATED)

class RemoveProjectIdeaImage(APIView):
    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, idea_pk):

        return Response()
