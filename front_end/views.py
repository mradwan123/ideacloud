from django.shortcuts import render, redirect
from projects.models import ProjectIdea
from front_end.form import RegisterForm
from users.serializers import UserSerializer
from django.contrib.auth import authenticate, login

# Create your views here.

def home(request):
    response = ProjectIdea.objects.all()
    return render(request, "home.html", context={"ideas": response})

def project_ideas(request):
    return render(request, "project_ideas.html")

def project_details(request):
    return render(request, "project_details.html")

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
    registration_form = RegisterForm
    if request.method == "POST":
        serializer = UserSerializer(data=request.POST)
        print(serializer.is_valid())
        print(serializer.errors)
        if serializer.is_valid():
            serializer.save()
            return redirect("front-end:login")
        else:
            return redirect("front-end:register")
    return render(request, "register.html", {"form": registration_form})

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

def completed_projects(request):
    return render(request, "completed_projects.html")

def project_groups(request):
    return render(request, "project_groups.html")

def interested_users(request):
    return render(request, "interested_users.html")

def comments(request):
    return render(request, "comments.html")
