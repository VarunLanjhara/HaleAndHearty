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

# def home(request,id,slug):
#     if request.method == "POST":
#         name = request.POST["name"]
#         email = request.POST["email"]
#         message = request.POST["message"]
#         contact = Contact(name=name,email=email,message=message)
#         contact.save()
#     else:
#         profile = Profile.objects.all()
#         followers = profile.followers.all()
#         numberoffollowers = len(followers)
#         for follower in followers:
#             if follower == request.user:
#                 isfollowing = True
#             else:
#                 isfollowing = False
#         post = get_object_or_404(Post,id = id,slug = slug)
#         if post.save.filer(id = request.user.id).exists():
#             issave = True;
#         context = {
#             "numberoffollowers":numberoffollowers,
#             "followers":followers,
#             "isfollowing":isfollowing,
#             "issave":issave
#         }
#         return render(request,"home.html",context)

# def save_post(self,request,pk):
#     post = Post.objects.get(pk = pk)
#     if post.save.filter(pk = request.user.pk).exists():
#         post.save.remove(request.user)
#     else:
#         post.save.add(request.user)
#     return HttpResponse("/")

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
            return redirect(f"/profile/{request.user.pk}")
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

class Profilee(View,LoginRequiredMixin):
    def get(self,request,pk):
        profile = Profile.objects.get(pk=pk)
        comment = Comment.objects.get(pk = pk)
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

    # def get_object(self):
    #     username = self.kwargs.get("username")
    #     return get_object_or_404(User,username = username)

class PostListView(View):
    def get(self,request,*args,**kwargs):
        posts = Post.objects.all()
        posts.order_by("-created")
        context = {
            "posts":posts,
        }
        return render(request,"home.html",context)

    def post(self,request):
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        contact = Contact(name=name,email=email,message=message)
        contact.save()
        return redirect("/")

class PostDetailview(View):
    def get(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()
        commentss = Comment.objects.filter(post=post)
        numberofcomments = len(commentss)
        

        comments = Comment.objects.filter(post=post).order_by('-commented')

        context = {
            "form":form,
            "post":post,
            'comments':comments,
            'numberofcomments':numberofcomments
        }

        return render(request,"post_detail.html",context)

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


    # def post(self,request):
    #     comment = request.POST.get("comment")
    #     user = request.user
    #     postid = request.POST.get("postid")
    #     post = Post.objects.get(id = postid)

    #     answer = Answer(comment = comment,user = user,post= post)
    #     answer.save()
    #     return redirect("/")


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

    # def get_object(self):
    #     title = self.kwargs.get("title")
    #     return get_object_or_404(Post,title = title)


class PostDeleteView(DeleteView,UserPassesTestMixin,LoginRequiredMixin):
    model = Post
    success_url = reverse_lazy("home")
    template_name = "post_delete.html"
    queryset = Post.objects.all()

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author;

    # def get_object(self):
    #     title = self.kwargs.get("title")
    #     return get_object_or_404(Post,title = title)
class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = Profile.objects.get(pk=pk)
        profile.followers.add(request.user)

        return redirect('profile', pk=profile.pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = Profile.objects.get(pk=pk)
        profile.followers.remove(request.user)

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
            # comment.user.profile.coins += 1
            # comment.user.profile.save()
            comment.dislikes.remove(request.user)

        isliked = False

        for like in comment.likes.all():
            if like == request.user:
                isliked = True
                break

        if not isliked:
            # comment.user.profile.coins += 1
            # comment.user.profile.save()
            comment.likes.add(request.user)
        if isliked:
            # comment.user.profile.coins -= 1
            # comment.user.profile.save()
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
            # comment.user.profile.coins -= 1
            # comment.user.profile.save() 
            comment.likes.remove(request.user)

        isdisliked = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                isdisliked = True
                break

        if not isdisliked:
            # comment.user.profile.coins -= 1
            # comment.user.profile.save()
            comment.dislikes.add(request.user)
        if isdisliked:
            # comment.user.profile.coins += 1
            # comment.user.profile.save()
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
            post.favourite.add(request.user)
        if is_favourite:
            post.favourite.remove(request.user)
        return redirect(f'/posts/{post.pk}')

def favouratelist(request):
    haha = Post.objects.filter(favourite = request.user)
    return render(request,"favouritelist.html",{"haha":haha})

def notificationstuff(request):
    user = request.user
    notification = Notifications.objects.filter(user = user).order_by("-date")
    return render(request,"notifications.html",{"notification":notification})