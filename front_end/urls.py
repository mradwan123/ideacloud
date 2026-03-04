from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    home,
    project_ideas,
    project_details,
    user_login,
    register,
    user_profile,
    about,
    create_project,
    favourite_projects,
    add_favourite_project,
    remove_favourite_project,
    saved_projects,
    finished_project,
    project_groups,
    interested_users,
    comments
)

app_name = "front-end"
urlpatterns = [
    path("", home, name="home"),
    path("project_ideas/", project_ideas, name="project-ideas"),
    # to be changed to "project_details/<int: id>"
    path("project_details/<int:pk>", project_details, name="project-details"),
    path("project_details/<int:pk>/add_favourite", add_favourite_project, name="add-favourite"),
    path("project_details/<int:pk>/remove_favourite", remove_favourite_project, name="remove-favourite"),
    path("login/", user_login, name="login"),
    path("register/", register, name="register"),
    path("user_profile/", user_profile, name="user-profile"),
    path("about/", about, name="about"),
    path("create_project/", create_project, name="create-project"),
    path("favourite_projects/", favourite_projects, name="favourite-projects"),
    path("saved_projects/", saved_projects, name="saved-projects"),
    path("completed_projects/", finished_project, name="completed-projects"),
    path("project_groups/", project_groups, name="project-groups"),
    path("interested_users/", interested_users, name="interested-users"),
    path("comments/", comments, name="comments")
]
