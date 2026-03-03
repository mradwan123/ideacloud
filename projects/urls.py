from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.test_view_to_display_images import test_image_view
from projects.views.view_project_idea import ProjectIdeaList, ProjectIdeaDetail
from projects.views.view_project_group import ProjectGroupList, ProjectGroupDetail
from projects.views.view_likes import ProjectIdeaToggleLike, FinishedProjectToggleLike

app_name = "projects"
urlpatterns = [
    ## ProjectIdea
    # Listing all ideas or create a new one
    path("project-ideas/", ProjectIdeaList.as_view(), name="project-idea-list"),
    # Access to methods related to a specific idea
    path("project-ideas/<int:idea_pk>/", ProjectIdeaDetail.as_view(), name="project-idea-detail"),

    ## ProjectGroup
    # Listing all groups under an idea or create a new one
    path("project-ideas/<int:idea_pk>/project-groups/", ProjectGroupList.as_view(), name="project-group-list"),
    # Access to methods related to a specific group
    path("project-ideas/<int:idea_pk>/project-groups/<int:group_pk>/", ProjectGroupDetail.as_view(), name="project-group-detail"),

    ##Likes
    # Toggling a user's like on Project Ideas
    path("project-ideas/<int:idea_pk>/like/", ProjectIdeaToggleLike.as_view(), name="project-idea-like"),
    # Toggling a user's like on Finished Projects
    path("finished-projects/<int:project_pk>/like/", FinishedProjectToggleLike.as_view(), name="finished-project-like"),

    ## Images
    # testing view for images
    path("test_image/", view=test_image_view, name="image_test"),
]
