from django.urls import path,include
from main import views
from main.views import AddFollower, PasswordResetVieww, PostListView, RemoveFollower, update_profile
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView,PasswordResetConfirmView,PasswordResetCompleteView
from main.views import PostCreateView,PostDetailview,PostUpdateView,PostDeleteView
urlpatterns = [
    path('password_reset/',PasswordResetVieww.as_view(),name = "password_reset"),
    path('password_reset/done/',PasswordResetDoneView.as_view(template_name = "reset/password_reset_done.html"),name = "password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/',PasswordResetConfirmView.as_view(template_name = "reset/password_reset_confirm.html"),name = "password_reset_confirm"),
    path('password_reset/complete/',PasswordResetCompleteView.as_view(template_name = "reset/password_reset_complete.html"),name = "password_reset_complete"),
    path('login/',views.loginUser,name = "login"),
    path('register/',views.registerUser,name = "register"),
    path('logout/',views.logoutUser,name = "logout"),
    path('update_profile/',views.update_profile,name = 'update_profile'),
    path('ask_question/',PostCreateView.as_view(),name = "ask_question"),
    path('',PostListView.as_view(),name = "home"),
    path('posts/<int:pk>/',PostDetailview.as_view(),name = "post_detail"),
    path('posts/<int:pk>/update/',PostUpdateView.as_view(),name = "post_update"),
    path('posts/<int:pk>/delete/',PostDeleteView.as_view(),name = "post_delete"),
    path('profile/<int:pk>/followers/add/',AddFollower.as_view(),name = "add_followers"),
    path('profile/<int:pk>/followers/remove/',RemoveFollower.as_view(),name = "remove_followers"),
]
