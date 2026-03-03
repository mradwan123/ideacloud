from rest_framework.decorators import api_view
from projects.models import ProjectIdea
from django.contrib.auth import get_user_model
from ..serializers.serializer_image_project import ImageProjectSerializer
from django.http import HttpResponse

@api_view(["POST",])
def test_image_view(request):
    User = get_user_model()
    user = User.objects.create_user(username="test_dev1", password="password")
    project_idea = ProjectIdea.objects.create(title="Test Project",
                                              description="Testing image serialization",
                                              author=user)
    base64_image = request.data.get("image")
    if base64_image:
        data = {"project_idea": project_idea.id,
                "image": base64_image}
        serializer = ImageProjectSerializer(data=data)
        if serializer.is_valid():
            image_instance = serializer.save()

            return HttpResponse(f'<img src="{image_instance.image.url}" alt="test image">')
    
    
    user.delete()
    project_idea.delete()

    return HttpResponse("no image found")
