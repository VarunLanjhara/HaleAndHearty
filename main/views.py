from django.conf.urls import url
from django.urls.base import reverse_lazy
from main.forms import RegisterForm
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView,PasswordResetConfirmView,PasswordResetCompleteView
from main.models import Contact,Profile
from main.forms import ProfileUpdateForm,UserUpdateForm,PostCreateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView,CreateView,ListView,UpdateView,DeleteView,View
import json
from django.contrib.auth.models import User
from main.models import Post
from django.urls import reverse
import requests

def loginUser(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:       
        if request.method == "POST":
                username = request.POST["username"]
                password = request.POST["password"]
                user = authenticate(request,username=username,password=password)

                if user is not None:
                    login(request,user)
                    return redirect("/")
                else:
                    return redirect("/login")
    return render(request,"login.html")

def registerUser(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            clientkey = request.POST["g-recaptcha-response"]
            secretkey = "6LeNBC0cAAAAAA8EXQ4L-zP58DTqlRG2dlzxRgbo"
            captchadata = {
                "secret":secretkey,
                "response":clientkey
            }
            r = requests.post("https://www.google.com/recaptcha/api/siteverify",data = captchadata)
            response = json.loads(r.text)
            verify = response["success"]
            if verify:
                register = RegisterForm(request.POST)
                if register.is_valid():
                    register.save()
                    username = register.cleaned_data.get("username")
                    return redirect("/login")
            else:
                print("Verify I Am Not A Robot")
                return redirect("/register")
        else:     
            register = RegisterForm()
        return render(request,"register.html",{"register":register})

def home(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        message = request.POST["message"]
        contact = Contact(name=name,email=email,message=message)
        contact.save()
    else:
        return render(request,"home.html")

def logoutUser(request):
    logout(request)
    return redirect('/login')

def update_profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST ,instance = request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES , instance = request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect(f"/profile/{request.user.profile}")
        else:
            return redirect("update_profile")
    else: 
        u_form = UserUpdateForm(instance = request.user)
        p_form = ProfileUpdateForm(instance = request.user.profile)
    context = {
        "u_form" : u_form,
        "p_form" : p_form
    }
    return render(request,"update_profile.html",context)

class PasswordResetVieww(PasswordResetView):
    template_name = "reset/password_reset.html"

class Profilee(DetailView,LoginRequiredMixin):
    login_url = "/login"
    template_name = "profile.html"
    queryset = User.objects.all()

    def get_object(self):
        username = self.kwargs.get("username")
        return get_object_or_404(User,username = username)

class PostListView(ListView):
    model = Post
    template_name = "home.html"
    context_object_name = "posts"
    ordering = ['-created'] 

    def post(self,request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        contact = Contact(name=name,email=email,message=message)
        contact.save()
        return redirect("/")

class PostDetailview(DetailView):
    model = Post
    queryset = Post.objects.all()
    template_name = "post_detail.html"

    def get_object(self):
        title = self.kwargs.get("title")
        return get_object_or_404(Post,title = title)

class PostCreateView(CreateView,LoginRequiredMixin):
    model = Post
    fields = ["title","body"]
    context_object_name = "create"
    template_name = "askquestion.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(UpdateView,UserPassesTestMixin,LoginRequiredMixin):
    model = Post
    fields = ["title","body"]
    context_object_name = "create"
    template_name = "askquestion.html"
    success_url = reverse_lazy("home")
    queryset = Post.objects.all()

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = Post.objects.all()
        if self.request.user == post.author:
            return True
        return False

    def get_object(self):
        title = self.kwargs.get("title")
        return get_object_or_404(Post,title = title)


class PostDeleteView(DeleteView,UserPassesTestMixin,LoginRequiredMixin):
    model = Post
    success_url = reverse_lazy("home")
    template_name = "post_delete.html"
    queryset = Post.objects.all()

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author;

    def get_object(self):
        title = self.kwargs.get("title")
        return get_object_or_404(Post,title = title)