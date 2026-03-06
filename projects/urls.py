from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from projects.views.view_project_idea import ProjectIdeaList, ProjectIdeaDetail
from projects.views.view_project_group import ProjectGroupList, ProjectGroupDetail, ProjectGroupMembershipToggle
from projects.views.view_project_idea_images import AddProjectIdeaImage, RemoveProjectIdeaImage
from projects.views.view_finished_project import FinishedProjectList, FinishedProjectDetail
from projects.views.view_likes import ProjectIdeaToggleLike, FinishedProjectToggleLike

app_name = "projects"
urlpatterns = [
    ## ProjectIdea
    # Listing all ideas or create a new one
    path("project-ideas/", ProjectIdeaList.as_view(), name="project-idea-list"),
    # Access to methods related to a specific idea
    path("project-ideas/<int:idea_pk>/", ProjectIdeaDetail.as_view(), name="project-idea-detail"),
    path("project-ideas/<int:idea_pk>/add-image/", AddProjectIdeaImage.as_view(), name="project-idea-add-image"),
    path("project-ideas/<int:idea_pk>/remove-image/", RemoveProjectIdeaImage.as_view(), name="project-idea-remove-image"),

    ## ProjectGroup
    # Listing all groups under an idea or create a new one
    path("project-ideas/<int:idea_pk>/project-groups/", ProjectGroupList.as_view(), name="project-group-list"),
    # Access to methods related to a specific group
    path("project-ideas/<int:idea_pk>/project-groups/<int:group_pk>/", ProjectGroupDetail.as_view(), name="project-group-detail"),
    # Toggle join or leave a group
    path("project-ideas/<int:idea_pk>/project-groups/<int:group_pk>/toggle-membership/", ProjectGroupMembershipToggle.as_view(), name="project-group-toggle-membership"),

    ## FinishedProject
    # Listing all finished projects or create a new one
    path("finished-projects/", FinishedProjectList.as_view(), name="finished-project-list"),
    # Access to get/path/del methods related to a specific finished project
    path("finished-projects/<int:finished_pk>/", FinishedProjectDetail.as_view(), name="finished-project-detail"),

    ##Likes
    # Toggling a user's like on Project Ideas
    path("project-ideas/<int:idea_pk>/like/", ProjectIdeaToggleLike.as_view(), name="project-idea-like"),
    # Toggling a user's like on Finished Projects
    path("finished-projects/<int:project_pk>/like/", FinishedProjectToggleLike.as_view(), name="finished-project-like"),
]
