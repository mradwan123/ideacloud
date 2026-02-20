from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    home,
    project_ideas,
    project_details,
    login,
    register,
    user_profile,
    about,
    contact_us,
)

app_name = "front-end"
urlpatterns = [
    path("", home, name="home"),
    path("project_ideas/", project_ideas, name="project-ideas"),
    # to be changed to "project_details/<int: id>"
    path("project_details/", project_details, name="project-details"),
    path("login/", login, name="login"),
    path("register/", register, name="register"),
    path("user_profile/", user_profile, name="user-profile"),
    path("about/", about, name="about"),
    path("contact_us", contact_us, name="contact-us")
]
