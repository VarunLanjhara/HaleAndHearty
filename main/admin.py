from django.contrib import admin
from main.models import Contact,Profile,Post,Comment,Notifications

admin.site.register(Contact)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Notifications)