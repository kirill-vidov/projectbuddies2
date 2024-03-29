from django.contrib import admin
from .models import Categories, Post, Skills, Message, Profile, Portfolio, Notifications


admin.site.register(Categories)
admin.site.register(Skills)
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Profile)
admin.site.register(Portfolio)
admin.site.register(Notifications)
