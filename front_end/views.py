from django.shortcuts import render, redirect
from projects.models import ProjectIdea
from front_end.form import RegisterForm
from users.serializers import UserSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from projects.serializers.serializer_project_idea_serializer import ProjectIdeaSerializer
from django.shortcuts import get_object_or_404

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
    return render(request, "project_details.html", context={"idea": serializer.data})

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

def user_profile(request):
    return render(request, "user_profile.html")

def about(request):
    return render(request, "about.html")

@login_required(login_url="front-end:login")
def create_project(request):
    return render(request, "create_project.html")

def favourite_projects(request):
    return render(request, "favourite_projects.html")

def saved_projects(request):
    return render(request, "saved_projects.html")

def finished_project(request):
    return render(request, "completed_projects.html")

def project_groups(request):
    return render(request, "project_groups.html")

def interested_users(request):
    return render(request, "interested_users.html")

def comments(request):
    return render(request, "comments.html")
