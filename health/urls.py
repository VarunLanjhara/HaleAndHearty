from django.contrib import admin
from django.contrib.auth import views
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from main.views import Profilee

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include("main.urls")),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('profile/<str:username>/',Profilee.as_view(),name = "profile"),
] + static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
