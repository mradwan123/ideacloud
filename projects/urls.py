from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.test_view_to_display_images import test_image_view

app_name = "projects"
urlpatterns = [
    path("test_image/", view=test_image_view, name="image_test")
]
