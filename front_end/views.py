from django.shortcuts import render, redirect
from django.contrib import messages
from projects.models import ProjectIdea, ProjectIdeaComment, Tag, ImageProject
from front_end.form import RegisterForm
from users.serializers import UserSerializer
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from projects.serializers.serializer_project_idea_serializer import ProjectIdeaSerializer
from django.shortcuts import get_object_or_404
from users.models import User

# Create your views here.

def home(request):
    if request.user.is_authenticated:
        ideas = ProjectIdea.objects.all()
        serializer = ProjectIdeaSerializer(ideas, many=True)
        return render(request, "home.html", context={"ideas": serializer.data})
    return render(request, "home.html")

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
    has_liked = request.user in idea.likes.all()
    return render(
        request,
        "project_details.html",
        context={
            "idea": serializer.data,
            "has_favourited": has_favourited,
            "has_saved": has_saved,
            "has_liked": has_liked,
            "like_count": idea.likes.count()
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
    if request.method == "POST":
        # Get form data
        title = request.POST.get('title').strip()
        description = request.POST.get('description').strip()
        tags = request.POST.getlist('tags')  # Get list of selected tag IDs
        images = request.FILES.getlist('images')  # Get uploaded images

        # Validate required fields
        if not title:
            messages.error(request, 'Title and description are required.')
            return redirect('front-end:create-project')
        print(tags)
        data = {
            'title': title,
            'description': description,
            'tags': tags,
        }

        serializer = ProjectIdeaSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        project_idea = serializer.save(author=request.user)
        print(project_idea)

        # -----------------TODO : Check images for create project ----------------

        # Handle image uploads
        for image in images:
            ImageProject.objects.create(
                image=image,
                project_idea=project_idea
            )

        messages.success(request, 'Project created successfully!')
        return redirect("front-end:project-details", pk=project_idea.id)

    # GET request - show form with tags
    tags = Tag.objects.all().order_by('name')
    context = {
        'tags': tags
    }
    return render(request, "create_project.html", context)

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

@login_required(login_url="front-end:login")
def add_like(request, pk):
    idea = get_object_or_404(ProjectIdea, pk=pk)
    idea.likes.add(request.user)
    return redirect("front-end:project-details", pk=pk)

@login_required(login_url="front-end:login")
def remove_like(request, pk):
    idea = get_object_or_404(ProjectIdea, pk=pk)
    idea.likes.remove(request.user)
    return redirect("front-end:project-details", pk=pk)

@login_required(login_url="front-end:login")
def public_user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    return render(
        request,
        "user_profile.html",
        context={
            "profile_user": profile_user
        }
    )

@login_required(login_url="front-end:login")
def comments(request, pk):
    idea = get_object_or_404(ProjectIdea, pk=pk)
    comments = idea.project_idea_comments.all().select_related("user")
    return render(
        request,
        "comments.html",
        context={
            "idea": idea,
            "comments": comments
        }
    )

@login_required(login_url="front-end:login")
def add_comment(request, pk):
    idea = get_object_or_404(ProjectIdea, pk=pk)
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            ProjectIdeaComment.objects.create(
                user=request.user,
                project_idea=idea,
                content=content
            )
    return redirect("front-end:comments", pk=pk)

@login_required(login_url="front-end:login")
def remove_comment(request, comment_id):
    comment = get_object_or_404(ProjectIdeaComment, pk=comment_id)
    if request.user == comment.user or request.user.is_staff:
        comment.delete()
    return redirect("front-end:comments", pk=comment.project_idea.id)

@login_required(login_url="front-end:login")
def edit_comment(request, comment_id):
    comment = get_object_or_404(ProjectIdeaComment, pk=comment_id)
    if request.user != comment.user and not request.user.is_staff:
        return redirect("front-end:comments", pk=comment.project_idea.id)
    if request.method == "POST":
        new_content = request.POST.get("content", "").strip()
        if new_content:
            comment.content = new_content
            comment.save()
        return redirect("front-end:comments", pk=comment.project_idea.id)
    return render(request, "edit_comment.html", context={"comment": comment})

def finished_project(request):
    return render(request, "completed_projects.html")

def project_groups(request):
    return render(request, "project_groups.html")

def interested_users(request):
    return render(request, "interested_users.html")
