from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
    path('post/create/', views.post_create, name='post-create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post-edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post-delete'),
    path('register/', views.register, name='register'),
    path('api/posts/', views.PostListAPI.as_view(), name='api-post-list'),
    path('api/posts/<int:pk>/', views.PostDetailAPI.as_view(), name='api-post-detail'),
]
