from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(_("username"), max_length=30, null=False, unique=True)
    email = models.EmailField(_("email address"), max_length=255, null=False, unique=True)
    friends = models.ManyToManyField("self", through="Friend", through_fields=("user", "friend"))
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    def __str__(self):
        return self.email


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posted")
    wall_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    jwt_token = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
