from django.shortcuts import render, redirect
from projects.models import ProjectIdea
from front_end.form import RegisterForm
from users.serializers import UserSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from projects.serializers.serializer_project_idea_serializer import ProjectIdeaSerializer
from django.shortcuts import get_object_or_404
from users.models import User

# Create your views here.

# TODO after making "home.html"
# it will have a view for logged in and not logged in user
def home(request):
    ideas = ProjectIdea.objects.all()
    serializer = ProjectIdeaSerializer(ideas, many=True)
    return render(request, "home.html", context={"ideas": serializer.data})

@login_required(login_url="front-end:login")
def project_ideas(request):
    ideas = ProjectIdea.objects.all()
    serializer = ProjectIdeaSerializer(ideas, many=True)
    return render(request, "project_ideas.html", context={"ideas": serializer.data})

@login_required(login_url="front-end:login")
def project_details(request, pk):
    idea = get_object_or_404(ProjectIdea, pk=pk)
    serializer = ProjectIdeaSerializer(idea)
    # check if the user has favourited the idea
    has_favourited = idea in request.user.favorite_projects.all()
    has_saved = idea in request.user.interested_projects.all()
    return render(
        request,
        "project_details.html",
        context={
            "idea": serializer.data,
            "has_favourited": has_favourited,
            "has_saved": has_saved
        })

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("front-end:home")
        # TODO: process user errors
    return render(request, "login.html")

def register(request):
    registration_form = RegisterForm()
    if request.method == "POST":
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            return redirect("front-end:login")
        else:
            # TODO: process user errors
            return redirect("front-end:register")
    return render(request, "register.html", {"form": registration_form})

@login_required(login_url="front-end:login")
def user_profile(request):
    user = request.user
    return render(request, "user_profile.html", context={"user": user})

def about(request):
    return render(request, "about.html")

@login_required(login_url="front-end:login")
def create_project(request):
    return render(request, "create_project.html")

@login_required(login_url="front-end:login")
def favourite_projects(request):
    user = request.user
    favourites = user.favorite_projects.all()
    return render(request, "favourite_projects.html", context={"favourites": favourites})

@login_required(login_url="front-end:login")
def add_favourite_project(request, pk):
    idea = get_object_or_404(ProjectIdea, pk=pk)
    request.user.favorite_projects.add(idea)
    return redirect("front-end:project-details", pk=pk)

@login_required(login_url="front-end:login")
def remove_favourite_project(request, pk):
    idea = get_object_or_404(ProjectIdea, pk=pk)
    request.user.favorite_projects.remove(idea)
    return redirect("front-end:project-details", pk=pk)

@login_required(login_url="front-end:login")
def saved_projects(request):
    user = request.user
    saved = user.interested_projects.all()
    return render(request, "saved_projects.html", context={"saved": saved})

@login_required(login_url="front-end:login")
def add_saved_project(request, pk):
    idea = get_object_or_404(ProjectIdea, pk=pk)
    request.user.interested_projects.add(idea)
    return redirect("front-end:project-details", pk=pk)

@login_required(login_url="front-end:login")
def remove_saved_project(request, pk):
    idea = get_object_or_404(ProjectIdea, pk=pk)
    request.user.interested_projects.remove(idea)
    return redirect("front-end:project-details", pk=pk)

def finished_project(request):
    return render(request, "completed_projects.html")

def project_groups(request):
    return render(request, "project_groups.html")

def interested_users(request):
    return render(request, "interested_users.html")

def comments(request):
    return render(request, "comments.html")
