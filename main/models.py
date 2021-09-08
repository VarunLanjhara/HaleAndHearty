from django.db import models
from django.contrib.auth.models import User
from django.urls.base import reverse
from ckeditor.fields import RichTextField
from django.utils.timezone import now

class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    message = models.TextField()

    def __str__(self):
        return str(self.name)

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpg",upload_to = "profile_pics")
    about = models.TextField(default="I am nerd")
    location = models.CharField(max_length=100)
    usercreated = models.DateTimeField(default=now)
    followers = models.ManyToManyField(User,blank=True,related_name="followers") 

    def __str__(self):
        return str(self.user.username)

class Post(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    body = RichTextField(blank = True,null = True)
    created = models.DateTimeField(default=now)
    favourite = models.ManyToManyField(User,related_name="favourite",blank = True)

    def __str__(self):
        return str(self.title)

class Comment(models.Model):
    body = RichTextField(blank = True,null = True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    commented = models.DateTimeField(default=now)
    likes = models.ManyToManyField(User,blank=True,related_name="likes")
    dislikes = models.ManyToManyField(User,blank=True,related_name="dislikes")

    def __str__(self):
        return str(self.body)

class Notifications(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='post')
    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sender')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user')
    date = models.DateTimeField(default=now)

    def __str__(self):
        return str(self.post)