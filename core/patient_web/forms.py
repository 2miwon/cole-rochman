from dataclasses import field
from django.forms import ModelForm
from ..models import Post,Comment

class PostForm(ModelForm):
    class Meta:
        model = Post
        # fields = '__all__'
        fields = ['title','category','content', 'images']