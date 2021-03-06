from django.urls import path,include
from main import views
from main.views import AddFollower, PasswordResetVieww, PostListView, RemoveFollower, SavePost, update_profile,AddDislike,AddLikes
from main.views import PostCreateView,PostDetailview,PostUpdateView,PostDeleteView
urlpatterns = [
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
    path('posts/<int:post_pk>/comment/<int:pk>likes/',AddLikes.as_view(),name = "addlikes"),
    path('posts/<int:post_pk>/<int:pk>/dislikes/',AddDislike.as_view(),name = "adddislikes"),
    path('posts/<int:pk>/save/',SavePost.as_view(),name = "save_post"),
    path("savedposts/",views.favouratelist,name = "saveposts"),
    path('notifications/',views.notificationstuff,name = "notifications"),
    path('redeem/',views.reddemcoins,name = "reddemcoins"),
    path('aboutus/',views.about,name = "about"),
    path('search/',views.search,name = "search")
]
