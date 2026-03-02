from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.test_view_to_display_images import test_image_view
from projects.views.view_project_idea import ProjectIdeaList, ProjectIdeaDetail
from projects.views.view_project_group import ProjectGroupList, ProjectGroupDetail
from projects.views.view_finished_project import FinishedProject, FinishedProjectDetail

app_name = "projects"
urlpatterns = [
    ## ProjectIdea
    # Listing all ideas or create a new one
    path("project-ideas/", ProjectIdeaList.as_view(), name="project-idea-list"),
    # Access to methods related to a specific idea
    path("project-ideas/<int:idea_pk>/", ProjectIdeaDetail.as_view(), name="project-idea-detail"),
    # Listing all groups under an idea or create a new one
    path("project-ideas/<int:idea_pk>/project-groups/", ProjectGroupList.as_view(), name="project-group-list"),
    # Access to methods related to a specific group
    path("project-ideas/<int:idea_pk>/project-groups/<int:group_pk>/", ProjectGroupDetail.as_view(), name="project-group-detail"),

    ## FinishedProject
    # Listing all finished projects or create a new one
    path("finished-projects/", FinishedProject.as_view(), name="finished-project-list"),
    # Access to get/path/del methods related to a specific finished project
    path("finished-projects/<int:finished_pk>/", FinishedProjectDetail.as_view(), name="finished-project-detail"),
    

    ## Images
    # testing view for images
    path("test_image/", view=test_image_view, name="image_test"),
]