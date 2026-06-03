from rest_framework import serializers
from .models import Post
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username']


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model            = Post
        fields           = ['id', 'title', 'content', 'author', 'published', 'created_at']
        read_only_fields = ['author', 'created_at']
