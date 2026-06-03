from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model  = Post
        fields = ['title', 'content', 'published']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter post title',
                'style': 'width:100%; padding:8px; margin-bottom:10px;'
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'Write your post here...',
                'rows': 10,
                'style': 'width:100%; padding:8px;'
            }),
        }
