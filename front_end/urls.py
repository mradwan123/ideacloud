from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    home,
    project_ideas,
    project_details,
    user_login,
    user_logout,
    register,
    user_profile,
    about,
    create_project,
    favourite_projects,
    add_favourite_project,
    remove_favourite_project,
    saved_projects,
    add_saved_project,
    remove_saved_project,
    add_like,
    remove_like,
    public_user_profile,
    comments,
    add_comment,
    remove_comment,
    edit_comment,
    finished_project,
    project_groups,
    interested_users
)

app_name = "front-end"
urlpatterns = [
    path("", home, name="home"),
    # project related links (project ideas, project details, create project)
    path("project_ideas/", project_ideas, name="project-ideas"),
    path("project_details/<int:pk>", project_details, name="project-details"),
    path("create_project/", create_project, name="create-project"),
    # favourite
    path("favourite_projects/", favourite_projects, name="favourite-projects"),
    path("project_details/<int:pk>/add_favourite", add_favourite_project, name="add-favourite"),
    path("project_details/<int:pk>/remove_favourite", remove_favourite_project, name="remove-favourite"),
    # saved
    path("saved_projects/", saved_projects, name="saved-projects"),
    path("project_details/<int:pk>/add_saved", add_saved_project, name="add-saved"),
    path("project_details/<int:pk>/remove_saved", remove_saved_project, name="remove-saved"),
    # like
    path("project_details/<int:pk>/add_like", add_like, name="add-like"),
    path("project_details/<int:pk>/remove_like", remove_like, name="remove-like"),
    # comments
    path("comments/<int:pk>", comments, name="comments"),
    path("comments/<int:pk>/add_comment", add_comment, name="add-comment"),
    path("comments/<int:comment_id>/remove_comment", remove_comment, name="remove-comment"),
    path("comments/<int:comment_id>/edit_comment", edit_comment, name="edit-comment"),
    # login / register / logout
    path("login/", user_login, name="login"),
    path("register/", register, name="register"),
    path("logout/", user_logout, name="logout"),
    # user profile / public user profile
    path("user_profile/", user_profile, name="user-profile"),
    path("user_profile/<int:user_id>", public_user_profile, name="public-user-profile"),
    # about section
    path("about/", about, name="about"),
    path("completed_projects/", finished_project, name="completed-projects"),
    path("project_groups/", project_groups, name="project-groups"),
    path("interested_users/", interested_users, name="interested-users")
]
