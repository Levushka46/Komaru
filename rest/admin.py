from django.contrib import admin
from .models import User, Friend, Post, Session

admin.site.register(User)
admin.site.register(Friend)
admin.site.register(Post)
admin.site.register(Session)
# Register your models here.
