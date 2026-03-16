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
    delete_project,
    remove_saved_project,
    add_like,
    remove_like,
    public_user_profile,
    comments,
    add_comment,
    remove_comment,
    edit_comment,
    finished_project_list,
    finished_project_detail,
    project_groups,
    add_image_to_project_idea,
    remove_image_from_project_idea,
    create_new_project_group,
    interested_users,
    group_details,
    join_group,
    leave_group,
    user_availability, 
)

app_name = "front-end"
urlpatterns = [
    path("", home, name="home"),
    # project related links (project ideas, project details, project images,  create project, finished project list and details)
    path("project_ideas/", project_ideas, name="project-ideas"),
    path("project_details/<int:pk>", project_details, name="project-details"),
    path("create_project/", create_project, name="create-project"),
    path("finished_projects/", finished_project_list, name="finished-projects"),
    path("finished_project_details/<int:pk>", finished_project_detail, name="finished-project-details"),
    # handle project images
    path("project_details/<int:idea_pk>/add_image_to_project", add_image_to_project_idea, name="add-image-to-project"),
    path("project_details/<int:idea_pk>/remove_image_from_project/<int:image_pk>", remove_image_from_project_idea, name="remove-image-from-project"),
    # favourite
    path("favourite_projects/", favourite_projects, name="favourite-projects"),
    path("project_details/<int:pk>/add_favourite", add_favourite_project, name="add-favourite"),
    path("project_details/<int:pk>/remove_favourite", remove_favourite_project, name="remove-favourite"),
    # saved
    path("saved_projects/", saved_projects, name="saved-projects"),
    path("project_details/<int:pk>/add_saved", add_saved_project, name="add-saved"),
    path("project_details/<int:pk>/remove_saved", remove_saved_project, name="remove-saved"),
    #delete 
    path("delete_project/<int:pk>", delete_project, name="delete-project"),
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
    # user available yes/no
    path("user_profile/<int:user_id>/availability/", user_availability, name="user-availability"),
    # about section
    path("about/", about, name="about"),

    # groups
    path("project_groups/<int:pk>/", project_groups, name="project-groups"),
    path("project_groups/<int:pk>/create_new_project_group/", create_new_project_group, name="create-new-project-group"),
    path("group_details/<group_id>/", group_details, name="group-details"),
    path("group_details/<group_id>/join_group/", join_group, name="join-group"),
    path("group_details/<group_id>/leave_group/", leave_group, name="leave-group"),

    path("interested_users/<int:pk>/", interested_users, name="interested-users"),
]
