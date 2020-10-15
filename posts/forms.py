from django.forms import ModelForm
from django import forms
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
<<<<<<< HEAD
        fields = ['group', 'text', 'image'] 


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        
=======
        fields = ['group', 'text']
>>>>>>> caec63caee2c86f618678ac33916de06e5a95b81
