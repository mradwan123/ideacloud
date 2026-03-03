from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.test_view_to_display_images import test_image_view
from projects.views.view_project_idea import ProjectIdeaList, ProjectIdeaDetail
from projects.views.view_project_group import ProjectGroupList, ProjectGroupDetail
from projects.views.view_project_idea_images import AddProjectIdeaImage,RemoveProjectIdeaImage

app_name = "projects"
urlpatterns = [
    ## ProjectIdea
    # Listing all ideas or create a new one
    path("project-ideas/", ProjectIdeaList.as_view(), name="project-idea-list"),
    # Access to methods related to a specific idea
    path("project-ideas/<int:idea_pk>/", ProjectIdeaDetail.as_view(), name="project-idea-detail"),
    path("project-ideas/<int:idea_pk>/add-image/", AddProjectIdeaImage.as_view(), name="project-idea-add-image"),
    path("project-ideas/<int:idea_pk>/remove-image/", RemoveProjectIdeaImage.as_view(), name="project-idea-remove-image"),
    # Listing all groups under an idea or create a new one
    path("project-ideas/<int:idea_pk>/project-groups/", ProjectGroupList.as_view(), name="project-group-list"),
    # Access to methods related to a specific group
    path("project-ideas/<int:idea_pk>/project-groups/<int:group_pk>/", ProjectGroupDetail.as_view(), name="project-group-detail"),

    ## Images
    # testing view for images
    path("test_image/", view=test_image_view, name="image_test"),
]