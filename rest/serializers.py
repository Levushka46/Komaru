from rest import exceptions
from .models import User, Post
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.serializers import Serializer, CharField, ModelSerializer, IntegerField
from rest_framework import serializers


class BaseUserSerializer(ModelSerializer):
    def create(self, validated_data):
        try:
            validate_password(validated_data["password"])
        except ValidationError:
            raise serializers.ValidationError()

        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email", "password"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
        }


class FriendListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        read_only_fields = ["id", "username", "email"]


class PostSerializer(ModelSerializer):
    post_id = serializers.IntegerField(read_only=True, source="id")
    author = serializers.CharField(read_only=True, source="user.username")

    class Meta:
        model = Post
        fields = ["post_id", "title", "content", "author"]
