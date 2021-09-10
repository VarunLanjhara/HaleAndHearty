from django.conf.urls import url
from django.urls.base import reverse_lazy
from main.forms import CommentForm, RegisterForm
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView,PasswordResetConfirmView,PasswordResetCompleteView
from main.models import Comment, Contact,Profile,Notifications
from main.forms import ProfileUpdateForm,UserUpdateForm,PostCreateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView,CreateView,ListView,UpdateView,DeleteView,View
import json
from django.contrib.auth.models import User
from main.models import Post
from django.urls import reverse
from django.contrib.messages.views import SuccessMessageMixin
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
    return render(request,"loginn.html")

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
                    messages.success(request,f"{username} Your Account Created Successfully")
                    return redirect("/login")
                else:
                    messages.warning(request,f"{register.errors}")
                    return redirect("/register")
            else:
                messages.warning(request,"Fill Recaptcha")
                return redirect("/register")
        else:     
            register = RegisterForm()
        return render(request,"registerr.html",{"register":register})

def logoutUser(request):
    logout(request)
    return redirect('/login')

def update_profile(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            u_form = UserUpdateForm(request.POST ,instance = request.user)
            p_form = ProfileUpdateForm(request.POST, request.FILES , instance = request.user.profile)

            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request,"Profile Updated Succesfully")
                return redirect(f"/profile/{request.user.pk}")
            else:
                messages.warning(request,"Fill All The Fields Correctly")
                return redirect("update_profile")
        else: 
            u_form = UserUpdateForm(instance = request.user)
            p_form = ProfileUpdateForm(instance = request.user.profile)
        context = {
            "u_form" : u_form,
            "p_form" : p_form
        }
        return render(request,"update_profile.html",context)
    else:
        return redirect("/")

class PasswordResetVieww(PasswordResetView):
    template_name = "reset/password_reset.html"

class Profilee(View,LoginRequiredMixin):
    def get(self,request,pk):
        if request.user.is_authenticated:
            profile = Profile.objects.get(pk=pk)
            comment = Comment.objects.all()
            user = profile.user
            posts = Post.objects.filter(author=user).order_by('-created')
            followers = profile.followers.all()
            number_of_followers = len(followers)
            if len(followers) == 0:
                is_following = False
            for follower in followers:
                if follower == request.user:
                    is_following = True
                    break
                else:
                    is_following = False

            context = {
                "profile":profile,
                'user':user, 
                'comment':comment,
                'posts':posts,
                'number_of_followers': number_of_followers,
                'is_following': is_following,
            }
            return render(request,"profile.html",context)
        else:
            return redirect("/")

class PostListView(ListView,LoginRequiredMixin):
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

class PostDetailview(View,LoginRequiredMixin):
    def get(self,request,pk,*args,**kwargs):
        if request.user.is_authenticated:
            post = Post.objects.get(pk=pk)
            form = CommentForm()
            commentss = Comment.objects.filter(post=post)
            numberofcomments = len(commentss)
            haha = Post.objects.filter(favourite = request.user)
            

            comments = Comment.objects.filter(post=post).order_by('-commented')

            context = {
                "form":form,
                "post":post,
                'comments':comments,
                'numberofcomments':numberofcomments,
                'haha':haha
            }

            return render(request,"post_detail.html",context)
        else:
            return redirect("/")

    def post(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = post
            new_comment.save()
            notification = Notifications(post = post,user = post.author,sender = new_comment.user)
            notification.save()
            messages.success(request,"Answer Added Successfully")
            return redirect(f"/posts/{post.pk}")
        commentss = Comment.objects.all()
        numberofcomments = len(commentss)

        comments = Comment.objects.filter(post=post).order_by('-commented')

        context = {
            "form":form,
            "post":post,
            'comments':comments,
            'numberofcomments':numberofcomments
        }

        return render(request,"post_detail.html",context)


class PostCreateView(SuccessMessageMixin,LoginRequiredMixin,CreateView):
    model = Post
    login_url = "/"
    fields = ["title","body"]
    template_name = "askquestion.html"
    success_url = reverse_lazy("home")
    success_message = "Question Asked Successfully"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(SuccessMessageMixin,LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = Post
    fields = ["title","body"]
    template_name = "askquestion.html"
    success_url = reverse_lazy("home")
    success_message = "Question Updated Successfully"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(SuccessMessageMixin,LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    success_url = reverse_lazy("home")
    template_name = "post_delete.html"
    success_message = "Question Deleted Successfully"

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = Profile.objects.get(pk=pk)
        profile.followers.add(request.user)
        messages.success(request,f"You Follow {profile.user}")
        return redirect('profile', pk=profile.pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = Profile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        messages.success(request,f"You Unfollow {profile.user}")
        return redirect('profile', pk=profile.pk)

class AddLikes(View):
    def post(self,request,pk,*args,**kwargs):
        comment = Comment.objects.get(pk=pk)

        isdisliked = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                isdisliked = True
                break

        if isdisliked:
            messages.success(request,"DisLike Removed Successfully")
            comment.dislikes.remove(request.user)

        isliked = False

        for like in comment.likes.all():
            if like == request.user:
                isliked = True
                break

        if not isliked:
            messages.success(request,"Like Added Successfully")
            comment.likes.add(request.user)
        if isliked:
            messages.success(request,"Like Removed Successfully")
            comment.likes.remove(request.user)

        likesoncommnet = comment.likes.count() - comment.dislikes.count()
        comment.user.profile.coins = likesoncommnet
        comment.user.profile.save()

        next = request.POST.get("next",'/')
        return HttpResponseRedirect(next)

class AddDislike(View):
    def post(self,request,pk,*args,**kwargs):
        comment = Comment.objects.get(pk=pk)

        isliked = False

        for like in comment.likes.all():
            if like == request.user:
                isliked = True
                break

        if isliked:
            messages.success(request,"Like Removed Successfully")
            comment.likes.remove(request.user)

        isdisliked = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                isdisliked = True
                break

        if not isdisliked:
            messages.success(request,"DisLike Added Successfully")
            comment.dislikes.add(request.user)
        if isdisliked:
            messages.success(request,"DisLike Removed Successfully")
            comment.dislikes.remove(request.user)
        
        likesoncommnet = comment.likes.count() - comment.dislikes.count()
        comment.user.profile.coins = likesoncommnet
        comment.user.profile.save()

        next = request.POST.get("next",'/')
        return HttpResponseRedirect(next)

class SavePost(View):
    def post(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk = pk)

        is_favourite = False

        for favourite in post.favourite.all():
            if favourite == request.user:
                is_favourite = True
                break
        if not is_favourite:
            messages.success(request,"Post Saved Successfully")
            post.favourite.add(request.user)
        if is_favourite:
            messages.success(request,"Post UnSaved Successfully")
            post.favourite.remove(request.user)
        return redirect(f'/posts/{post.pk}')

def favouratelist(request):
    if request.user.is_authenticated:
        haha = Post.objects.filter(favourite = request.user)
        return render(request,"favouritelist.html",{"haha":haha})
    else:
        return redirect("/")

def notificationstuff(request):
    if request.user.is_authenticated:
        user = request.user
        notification = Notifications.objects.filter(user = user).order_by("-date")
        return render(request,"notifications.html",{"notification":notification})
    else:
        return redirect("/")


def reddemcoins(request):
    if request.user.is_authenticated:
        return render(request,"reddem.html")
    else:
        return redirect("/")

def about(request):
    if request.user.is_authenticated:
        return render(request,"about.html")
    else:
        return redirect("/#about")

def search(request):
    return HttpResponse("Bhv")