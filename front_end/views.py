from django.shortcuts import render
from projects.models import ProjectIdea

# Create your views here.

def home(request):
    response = ProjectIdea.objects.all()
    return render(request, "home.html", context={"ideas": response})

def project_ideas(request):
    return render(request, "project_ideas.html")

def project_details(request):
    return render(request, "project_details.html")

def login(request):
    return render(request, "login.html")

def register(request):
    return render(request, "register.html")

def user_profile(request):
    return render(request, "user_profile.html")

def about(request):
    return render(request, "about.html")

def create_project(request):
    return render(request, "create_project.html")

def favourite_projects(request):
    return render(request, "favourite_projects.html")

def saved_projects(request):
    return render(request, "saved_projects.html")
