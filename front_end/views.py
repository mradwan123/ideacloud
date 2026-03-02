from django.shortcuts import render, redirect
from projects.models import ProjectIdea
from users.form import RegisterForm

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
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('front-end:login')
    else:
        form = RegisterForm()
    return render(request, "register.html", {'form': form})

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
