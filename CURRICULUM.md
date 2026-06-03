# Django Deep Learning Curriculum
# Learn by Building: A Blog + API App

This curriculum teaches Django by building a real project step by step.
Each lesson explains the WHY, not just the HOW.

---

## PHASE 1 — Setup (Day 1)

### Step 1.1 — Install everything

Open your terminal and run:

```bash
# Check Python is installed
python --version        # should be 3.10+

# Create a folder for your project
mkdir myblog
cd myblog

# Create a virtual environment (isolated Python for this project)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install Django
pip install django

# Confirm it's installed
django-admin --version
```

WHY virtual environments?
Without one, every project shares the same packages.
If ProjectA needs Django 4.0 and ProjectB needs Django 5.0, they conflict.
A venv gives each project its own isolated space.

---

### Step 1.2 — Create your Django project

```bash
django-admin startproject myblog .
# The dot (.) means "create it in the current folder, not a subfolder"
```

You now have this structure:
```
myblog/
├── manage.py          <- your command center (run all commands through this)
├── myblog/
│   ├── __init__.py    <- tells Python this is a package (don't touch)
│   ├── settings.py    <- ALL configuration lives here
│   ├── urls.py        <- the main URL router
│   └── wsgi.py        <- used when deploying to a server
```

Run the server:
```bash
python manage.py runserver
```
Visit http://127.0.0.1:8000 — you should see the Django welcome page.

---

### Step 1.3 — Create your first app

A Django PROJECT is the whole website.
A Django APP is one feature/module inside that website.
You can have many apps inside one project.

Example: Instagram = project. Feed, Stories, Messages = separate apps.

```bash
python manage.py startapp blog
```

New folder created:
```
blog/
├── admin.py       <- register models to appear in the admin panel
├── apps.py        <- app configuration (rarely touched)
├── models.py      <- your database tables defined as Python classes
├── views.py       <- your logic (receives request, returns response)
├── urls.py        <- (you create this file) URL routes for this app
└── migrations/    <- database change history (auto-generated)
```

Now tell Django your app exists. Open myblog/settings.py and find INSTALLED_APPS:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',   # <-- add this line
]
```

---

## PHASE 2 — Models & Database (Day 2-3)

Models are Python classes that represent database tables.
Each class attribute = one column in the table.
Each instance of the class = one row in the table.

### Step 2.1 — Write your first model

Open blog/models.py and replace everything with:

```python
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    author     = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published  = models.BooleanField(default=False)

    def __str__(self):
        return self.title   # what shows in the admin panel

    class Meta:
        ordering = ['-created_at']  # newest posts first (- means descending)
```

Field types explained:
- CharField       -> short text, always needs max_length
- TextField       -> long text, no size limit
- ForeignKey      -> links to another table (many posts can have one author)
- DateTimeField(auto_now_add=True) -> set ONCE automatically when created
- DateTimeField(auto_now=True)     -> updated automatically every time you save
- BooleanField    -> True or False value

on_delete=models.CASCADE means:
  if the User is deleted, delete all their posts too.
Other options:
  SET_NULL  -> set author to null (field must allow null=True)
  PROTECT   -> block deletion of user if they have posts
  SET_DEFAULT -> set to a default value

---

### Step 2.2 — Run migrations

Migrations are how Django syncs your Python model with the real database.
Think of it as: model = blueprint, migration = construction plan, database = actual building.

```bash
# Step 1: Django reads your models and CREATES the migration files
python manage.py makemigrations

# Step 2: Django APPLIES those files to the actual database
python manage.py migrate
```

Rule to remember:
- Run makemigrations whenever you ADD or CHANGE a model
- Run migrate to apply those changes to the database
- Always run both together, in that order

---

### Step 2.3 — Django ORM (talking to the database)

ORM = Object Relational Mapper.
It lets you use Python to query the database instead of writing raw SQL.

Open the Django shell (Python + Django loaded together):
```bash
python manage.py shell
```

Try these commands:

```python
from blog.models import Post
from django.contrib.auth.models import User

# --- CREATE ---
user = User.objects.create_user(username='omar', password='test123')

post = Post.objects.create(
    title='My First Post',
    content='Hello world! This is my first Django post.',
    author=user,
    published=True
)

# --- READ (all) ---
Post.objects.all()
# returns: <QuerySet [<Post: My First Post>]>

# --- READ (filter) ---
Post.objects.filter(published=True)
Post.objects.filter(author=user)
Post.objects.filter(title__icontains='first')  # case-insensitive search

# --- READ (one) ---
Post.objects.get(id=1)
# WARNING: raises error if not found or if multiple found

# --- UPDATE ---
post = Post.objects.get(id=1)
post.title = 'Updated Title'
post.save()

# Or update without fetching first:
Post.objects.filter(id=1).update(title='Updated Title')

# --- DELETE ---
post.delete()

# --- COUNTING ---
Post.objects.filter(published=True).count()

# --- CHAINING ---
Post.objects.filter(published=True).order_by('-created_at')[:5]  # latest 5
```

SQL equivalent (so you understand what happens behind the scenes):
```sql
-- Post.objects.all()
SELECT * FROM blog_post;

-- Post.objects.filter(published=True)
SELECT * FROM blog_post WHERE published = true;

-- Post.objects.get(id=1)
SELECT * FROM blog_post WHERE id = 1;

-- Post.objects.filter(published=True).count()
SELECT COUNT(*) FROM blog_post WHERE published = true;
```

---

## PHASE 3 — Views & URLs (Day 4-6)

A VIEW receives an HTTP request and returns an HTTP response.
A URL PATTERN maps a URL to a view function.

Request flow:
User types URL -> Django checks urls.py -> finds matching view -> view runs -> returns HTML page

---

### Step 3.1 — Your first view

Open blog/views.py and replace everything with:

```python
from django.shortcuts import render, get_object_or_404
from .models import Post


def post_list(request):
    posts = Post.objects.filter(published=True)
    context = {
        'posts': posts,
        'title': 'All Posts'
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, published=True)
    return render(request, 'blog/post_detail.html', {'post': post})
```

What is the request object?
Every view receives a request object containing everything about the HTTP request:
- request.method   -> 'GET' or 'POST'
- request.user     -> the logged-in user (or AnonymousUser)
- request.GET      -> data from URL query params (?search=hello)
- request.POST     -> data submitted from a form

What is context?
A dictionary of variables you want to use in the template.
{'posts': posts} means inside the template you can write {{ posts }}.

What is get_object_or_404?
Tries to get the object from the database.
If it does not exist, it returns a clean 404 Not Found page.
Without it, Django would crash with an ugly 500 error page.
Always use this in detail views.

---

### Step 3.2 — URL routing

Create a NEW file: blog/urls.py

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
]
```

URL pattern syntax explained:
- ''                 -> matches /blog/ (the root of this app)
- 'post/<int:pk>/'  -> captures an integer from the URL and passes it as pk
- name='post-list'  -> gives this URL a name so templates can reference it

Now connect it to the main project. Open myblog/urls.py:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),  # add this line
]
```

include() tells Django: "any URL starting with blog/ -> hand it to blog/urls.py"

Full example:
User visits /blog/post/5/
-> Django sees it starts with blog/
-> Passes post/5/ to blog/urls.py
-> Matches post/<int:pk>/ with pk=5
-> Calls post_detail(request, pk=5)

---

### Step 3.3 — Templates

Templates are HTML files with special Django tags inside them.

Create this folder structure inside your blog folder:
```
blog/
└── templates/
    └── blog/
        ├── base.html
        ├── post_list.html
        └── post_detail.html
```

--- File: blog/templates/blog/base.html ---
This is the master layout. All other pages inherit from it.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}My Blog{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        nav { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
        nav a { margin-right: 15px; text-decoration: none; color: #333; }
        .post { border-bottom: 1px solid #ccc; padding: 20px 0; }
        .btn { padding: 8px 15px; background: #333; color: white; text-decoration: none; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <nav>
        <a href="{% url 'post-list' %}">Home</a>
        {% if user.is_authenticated %}
            <a href="{% url 'post-create' %}">New Post</a>
            <a href="{% url 'logout' %}">Logout ({{ user.username }})</a>
        {% else %}
            <a href="{% url 'login' %}">Login</a>
            <a href="{% url 'register' %}">Register</a>
        {% endif %}
    </nav>

    {% if messages %}
        {% for message in messages %}
            <div style="background:#d4edda; padding:10px; margin-bottom:10px;">{{ message }}</div>
        {% endfor %}
    {% endif %}

    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

--- File: blog/templates/blog/post_list.html ---

```html
{% extends 'blog/base.html' %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
    <h1>{{ title }}</h1>

    {% if posts %}
        {% for post in posts %}
            <div class="post">
                <h2>
                    <a href="{% url 'post-detail' post.pk %}">{{ post.title }}</a>
                </h2>
                <small>
                    By {{ post.author.username }} on {{ post.created_at|date:"F j, Y" }}
                </small>
                <p>{{ post.content|truncatewords:30 }}</p>
                <a href="{% url 'post-detail' post.pk %}">Read more</a>
            </div>
        {% endfor %}
    {% else %}
        <p>No posts published yet.</p>
    {% endif %}
{% endblock %}
```

--- File: blog/templates/blog/post_detail.html ---

```html
{% extends 'blog/base.html' %}

{% block title %}{{ post.title }}{% endblock %}

{% block content %}
    <h1>{{ post.title }}</h1>
    <small>By {{ post.author.username }} on {{ post.created_at|date:"F j, Y" }}</small>
    <hr>
    <p>{{ post.content }}</p>

    {% if user == post.author %}
        <a href="{% url 'post-edit' post.pk %}" class="btn">Edit</a>
        <a href="{% url 'post-delete' post.pk %}" class="btn" style="background:red;">Delete</a>
    {% endif %}

    <br><br>
    <a href="{% url 'post-list' %}">Back to all posts</a>
{% endblock %}
```

Template tags explained:
- {{ variable }}              -> outputs a value
- {% tag %}                   -> logic: if, for, extends, block, url
- {{ post.created_at|date:"F j, Y" }}  -> | is a filter, transforms the value
- {% url 'post-list' %}       -> generates the URL by its name
- {% extends 'base.html' %}   -> inherit the layout from base.html
- {% block content %}         -> defines a replaceable section

Common filters:
- {{ text|truncatewords:30 }} -> show only first 30 words
- {{ name|upper }}            -> UPPERCASE
- {{ name|lower }}            -> lowercase
- {{ date|date:"Y-m-d" }}    -> format a date
- {{ number|floatformat:2 }} -> round to 2 decimal places

---

## PHASE 4 — Django Admin (Day 7)

The admin is a free, auto-generated dashboard for managing your data.
It takes 5 lines of code to set up and saves hours of work.

### Step 4.1 — Register your model

Open blog/admin.py:

```python
from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display  = ['title', 'author', 'published', 'created_at']
    list_filter   = ['published', 'created_at']
    search_fields = ['title', 'content']
    list_editable = ['published']
```

list_display  -> which columns to show in the list view
list_filter   -> add filter sidebar on the right
search_fields -> enable search bar
list_editable -> edit directly from the list without opening each item

### Step 4.2 — Create a superuser

```bash
python manage.py createsuperuser
# Enter username, email, password when prompted
```

Visit http://127.0.0.1:8000/admin and log in.
You can now create, edit, and delete posts from a nice interface.

---

## PHASE 5 — Forms & Full CRUD (Day 8-10)

CRUD = Create, Read, Update, Delete.
We already have Read (list + detail views).
Now we add Create, Update, and Delete.

### Step 5.1 — ModelForm

Create a new file: blog/forms.py

```python
from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'published']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter post title',
                'style': 'width:100%; padding:8px;'
            }),
            'content': forms.Textarea(attrs={
                'rows': 10,
                'style': 'width:100%; padding:8px;'
            }),
        }
```

ModelForm automatically:
- Creates form fields from the model fields
- Handles validation (required fields, max_length, etc.)
- Can save directly to the database

---

### Step 5.2 — Create, Edit, Delete views

Add these to blog/views.py (keep the existing ones, add below):

```python
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post
from .forms import PostForm


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)  # create object but don't save yet
            post.author = request.user      # set author to logged-in user
            post.save()                     # now save to database
            messages.success(request, 'Post created successfully!')
            return redirect('post-detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Create'})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)  # bind form to existing post
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post-detail', pk=post.pk)
    else:
        form = PostForm(instance=post)  # pre-fill form with current data

    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Edit'})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('post-list')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})
```

IMPORTANT - The POST/Redirect/GET pattern:
1. User submits form -> POST request arrives
2. You process and save the data
3. You REDIRECT to another page (GET request)

Why? Without the redirect, if the user refreshes the page,
the browser re-sends the POST request and creates a duplicate!
Always redirect after a successful POST.

@login_required:
This decorator blocks unauthenticated users.
If not logged in, they get redirected to the login page automatically.

commit=False:
form.save(commit=False) creates the Python object but does NOT write to DB yet.
This lets you add extra data (like author) before saving.

---

### Step 5.3 — Form templates

--- File: blog/templates/blog/post_form.html ---

```html
{% extends 'blog/base.html' %}

{% block title %}{{ action }} Post{% endblock %}

{% block content %}
    <h1>{{ action }} Post</h1>

    <form method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn">{{ action }} Post</button>
        <a href="{% url 'post-list' %}">Cancel</a>
    </form>
{% endblock %}
```

--- File: blog/templates/blog/post_confirm_delete.html ---

```html
{% extends 'blog/base.html' %}

{% block content %}
    <h1>Delete Post</h1>
    <p>Are you sure you want to delete: <strong>{{ post.title }}</strong>?</p>

    <form method="POST">
        {% csrf_token %}
        <button type="submit" class="btn" style="background:red;">Yes, Delete</button>
        <a href="{% url 'post-detail' post.pk %}">Cancel</a>
    </form>
{% endblock %}
```

IMPORTANT - {% csrf_token %}:
This tag is MANDATORY inside every form that submits data.
It generates a hidden security token.
Without it, attackers could trick users into submitting forms from other websites.
Django will reject any POST request that does not have this token.

Update blog/urls.py to include the new URLs:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
    path('post/create/', views.post_create, name='post-create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post-edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post-delete'),
]
```

---

## PHASE 6 — Authentication (Day 11-12)

### Step 6.1 — Login & Logout

Django has login/logout views built-in. You just need templates and URLs.

Open myblog/urls.py:

```python
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', include('blog.urls')),  # we'll handle this in blog/urls.py
]
```

Add these lines to the bottom of myblog/settings.py:

```python
LOGIN_REDIRECT_URL  = '/blog/'   # where to go after login
LOGOUT_REDIRECT_URL = '/blog/'   # where to go after logout
LOGIN_URL           = '/login/'  # where to redirect unauthenticated users
```

--- File: blog/templates/blog/login.html ---

```html
{% extends 'blog/base.html' %}

{% block title %}Login{% endblock %}

{% block content %}
    <h1>Login</h1>

    <form method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn">Login</button>
    </form>

    <p>Don't have an account? <a href="{% url 'register' %}">Register here</a></p>
{% endblock %}
```

### Step 6.2 — Register view

Add to blog/views.py:

```python
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login


def register(request):
    if request.user.is_authenticated:
        return redirect('post-list')  # already logged in, go home

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # log them in immediately after registering
            messages.success(request, f'Welcome, {user.username}! Your account is ready.')
            return redirect('post-list')
    else:
        form = UserCreationForm()

    return render(request, 'blog/register.html', {'form': form})
```

Add to blog/urls.py:

```python
path('register/', views.register, name='register'),
```

--- File: blog/templates/blog/register.html ---

```html
{% extends 'blog/base.html' %}

{% block title %}Register{% endblock %}

{% block content %}
    <h1>Create Account</h1>

    <form method="POST">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn">Register</button>
    </form>

    <p>Already have an account? <a href="{% url 'login' %}">Login here</a></p>
{% endblock %}
```

---

## PHASE 7 — Django REST Framework / API (Day 13-16)

An API lets other apps (mobile apps, React, Vue) use your backend.
Instead of returning HTML, you return JSON data.

Install DRF:
```bash
pip install djangorestframework
```

Add to INSTALLED_APPS in settings.py:
```python
'rest_framework',
```

### Step 7.1 — Serializers

Serializers convert model instances to JSON and JSON back to model instances.
Think of them like forms, but for APIs instead of HTML.

Create blog/serializers.py:

```python
from rest_framework import serializers
from .models import Post
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)  # nested serializer

    class Meta:
        model        = Post
        fields       = ['id', 'title', 'content', 'author', 'published', 'created_at']
        read_only_fields = ['author', 'created_at']
```

### Step 7.2 — API Views

Add to blog/views.py:

```python
from rest_framework import generics, permissions
from .serializers import PostSerializer


class PostListAPI(generics.ListCreateAPIView):
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Post.objects.filter(published=True)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Post.objects.filter(published=True)
```

generics.ListCreateAPIView gives you:
- GET  /api/posts/    -> list all posts
- POST /api/posts/    -> create a new post

generics.RetrieveUpdateDestroyAPIView gives you:
- GET    /api/posts/1/  -> get one post
- PUT    /api/posts/1/  -> replace a post
- PATCH  /api/posts/1/  -> update part of a post
- DELETE /api/posts/1/  -> delete a post

All of this with just a few lines of code.

Add to blog/urls.py:

```python
path('api/posts/', views.PostListAPI.as_view(), name='api-post-list'),
path('api/posts/<int:pk>/', views.PostDetailAPI.as_view(), name='api-post-detail'),
```

Visit http://127.0.0.1:8000/blog/api/posts/
Django REST Framework gives you a beautiful browsable API page.
You can also test it with tools like Postman or Insomnia.

---

## PHASE 8 — Deployment (Day 17-18)

When your app is ready, here is how to prepare it for production.

### Step 8.1 — Settings changes

```python
# Never True in production - shows detailed errors to attackers
DEBUG = False

# Only allow requests from your domain
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Keep secret key in environment variable, NOT in code
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-only-for-dev')

# Database: switch from SQLite to PostgreSQL
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.environ.get('DB_NAME'),
        'USER':     os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST':     os.environ.get('DB_HOST', 'localhost'),
        'PORT':     os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### Step 8.2 — Install production packages

```bash
pip install gunicorn whitenoise psycopg2-binary

# Collect all static files into one folder
python manage.py collectstatic
```

### Step 8.3 — Easiest deployment options

1. Railway.app   -> free tier, connect GitHub, auto-deploy
2. Render.com    -> free tier, good for Django
3. PythonAnywhere -> beginner-friendly, has free tier

---

## QUICK REFERENCE — Commands You Will Use Every Day

```bash
python manage.py runserver            # start the development server
python manage.py startapp <name>      # create a new app
python manage.py makemigrations       # generate migration files after model changes
python manage.py migrate              # apply migrations to database
python manage.py createsuperuser      # create an admin user
python manage.py shell                # open Python shell with Django loaded
python manage.py collectstatic        # gather static files for production
python manage.py dbshell              # open the raw database shell
```

---

## WHAT TO BUILD AFTER THIS

Once you finish this curriculum and the blog app is working, we will build:

Project 2: Task Manager
- Multiple users with their own task lists
- Categories, priorities, due dates
- Mark tasks complete

Project 3: E-commerce Store
- Products, cart, checkout flow
- Image uploads
- Order history

Project 4: REST API + React Frontend
- Decouple backend from frontend
- JWT authentication
- Full modern web app architecture

---

## THE COMPLETE FILE STRUCTURE (when done)

```
myblog/
├── manage.py
├── myblog/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── blog/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── forms.py
    ├── serializers.py
    ├── admin.py
    └── templates/
        └── blog/
            ├── base.html
            ├── post_list.html
            ├── post_detail.html
            ├── post_form.html
            ├── post_confirm_delete.html
            ├── login.html
            └── register.html
```
