from django.shortcuts import render, redirect
from projects.models import ProjectIdea, Tag
from users.form import RegisterForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required



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
    if request.method == "POST":
        # Get form data
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        selected_tags = request.POST.getlist('tags')  # Get list of selected tag IDs
        images = request.FILES.getlist('images')  # Get uploaded images
        
        # Validate required fields
        if not title or not description:
            messages.error(request, 'Title and description are required.')
            tags = Tag.objects.all().order_by('name')
            return render(request, "create_project.html", {'tags': tags})
        
        try:
            # Create the project
            project = ProjectIdea.objects.create(
                title=title,
                description=description,
                author=request.user
            )
            
            # Add selected tags
            if selected_tags:
                project.tags.set(selected_tags)
            
            # Handle image uploads
            for image in images:
                ImageProject.objects.create(
                    image=image,
                    project_idea=project
                )
            
            messages.success(request, 'Project created successfully!')
            return redirect("front-end:project-details", pk=project.id)
            
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
    
    # GET request - show form with tags
    tags = Tag.objects.all().order_by('name')
    context = {
        'tags': tags
    }
    return render(request, "create_project.html", context)
    

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
