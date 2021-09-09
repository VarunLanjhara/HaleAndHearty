from django.contrib.auth import forms
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.db.models import fields
from main.models import Comment, Profile
from main.models import Post

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['username'].widget.attrs.update({'placeholder':('Username')})
            self.fields['email'].widget.attrs.update({'placeholder':('Email')})
            self.fields['password1'].widget.attrs.update({'placeholder':('Password')})        
            self.fields['password2'].widget.attrs.update({'placeholder':('Re-enter Password')})

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["image","location","about"]

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email']

class PostCreateView(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title","body"]
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']