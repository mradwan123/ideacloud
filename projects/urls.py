from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from projects.views.view_project_idea import ProjectIdeaList, ProjectIdeaDetail

app_name = "projects"
urlpatterns = [
    ## ProjectIdea
    # Listing all ideas or create a new one
    path("project-ideas/", ProjectIdeaList.as_view(), name="project-idea-list"),
    # Access to methods related to a specific idea
    path("project-ideas/<int:idea_pk>/", ProjectIdeaDetail.as_view(), name="project-idea-detail"),
]