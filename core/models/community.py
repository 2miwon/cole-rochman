<<<<<<< HEAD
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE
from django.utils import timezone


class Post(models.Model):
    CATEGORY_QUESTION = "question"
    CATEGORY_GENERAL = "general"
    CATEGORY_CHOICES = ((CATEGORY_QUESTION, "질문글"), (CATEGORY_GENERAL, "일반글"))
    category = models.CharField(max_length=20)
    anonymous = models.BooleanField(default = False)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    content = models.TextField()
    images = models.ImageField(blank=True, upload_to="images/", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    count_of_commnet = models.IntegerField(null=True, blank=True)
   


class Comment(models.Model):
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE )
    comment = models.TextField(max_length=200)
    created_at_comment =  models.DateField(auto_now_add=True,editable= False, null=True)
    updated_at_comment = models.DateField(auto_created=timezone.now)
    
=======
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.deletion import CASCADE
from django.utils import timezone


class Post(models.Model):
    CATEGORY_QUESTION = "question"
    CATEGORY_GENERAL = "general"
    CATEGORY_CHOICES = ((CATEGORY_QUESTION, "질문글"), (CATEGORY_GENERAL, "일반글"))
    category = models.CharField(max_length=20)
    anonymous = models.BooleanField(default = False)
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    print_created_at = models.CharField(max_length=10, default='', null=True, blank=True)
    count_of_comment = models.IntegerField(null=True, blank=True)
 


class Comment(models.Model):
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE )
    comment = models.TextField(max_length=200)
    created_at_comment = models.DateField(auto_now_add=True,editable= False, null=True)
    updated_at_comment = models.DateField(auto_created=timezone.now)
    print_created_at = models.CharField(max_length=10, default='', null=True, blank=True)

>>>>>>> 94078e6bd1f7a529379171d21e22fa4ba925ef86
