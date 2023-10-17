from django.shortcuts import render
from django.db import transaction
from django.db.models import Q, F
from .serializers import BaseUserSerializer, FriendListSerializer, PostSerializer
from .models import User, Friend, Post, Session
from rest import exceptions
from datetime import datetime, timedelta

from rest_framework import serializers
from rest_framework import mixins, status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    GenericAPIView,
)
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, ParseError, AuthenticationFailed, PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = BaseUserSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=["post"])
    def register(self, request: Request) -> Response:
        conflict_users = User.objects.filter(
            Q(email=request.data.get("email")) | Q(username=request.data.get("username"))
        )
        if conflict_users.exists():
            raise exceptions.ConflictError({"error": "Conflict", "message": "User already exists"})

        try:
            response = self.create(request)
        except serializers.ValidationError:
            raise serializers.ValidationError({"error": "Bad Request", "message": "Invalid data"})

        return Response(
            data={
                "message": "User registered successfully",
                "user_id": response.data["id"],
            },
            status=status.HTTP_201_CREATED,
        )


class LoginJWTView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except (TokenError, AuthenticationFailed):
            raise AuthenticationFailed({"error": "Unauthorized", "message": "Invalid credentials"})

        jwt_token = serializer.validated_data["access"]
        user = serializer.user

        Session.objects.filter(user=user, expires_at__lt=datetime.now()).delete()
        Session.objects.create(user=user, jwt_token=jwt_token, expires_at=datetime.now() + timedelta(minutes=5))

        access_token = f"Bearer {jwt_token}"
        return Response(
            {"message": "Logged in successfully", "username": request.data["username"]},
            status=status.HTTP_200_OK,
            headers={"Authorization": access_token},
        )


class UserProfileViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = BaseUserSerializer
    lookup_field = "username"

    def update(self, request: Request, *args, **kwargs) -> Response:
        if request.user.username != kwargs.get("username"):
            raise PermissionDenied({"error": "Forbidden", "message": "You can only update your profile"})
        return super().update(request, *args, **kwargs)


class FriendView(APIView):
    def post(self, request: Request, username=None) -> Response:
        user = request.user
        try:
            friend = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound({"error": "Not Found", "message": "User does not exist"})

        if user.id == friend.id:
            raise ParseError({"error": "Bad Request", "message": "Cannot make friends with yourself"})

        Friend.objects.create(user_id=user.id, friend_id=friend.id)
        return Response(
            {"message": "Friend added successfully", "friend_username": friend.username},
            status=status.HTTP_201_CREATED,
        )


class UnFriendView(APIView):
    def delete(self, request: Request, username=None) -> Response:
        user = request.user
        try:
            friendship = Friend.objects.get(user_id=user.id, friend__username=username)
        except Friend.DoesNotExist:
            raise NotFound({"error": "Not Found", "message": "Friend does not exist"})

        friendship.delete()
        return Response(
            {"message": "Friend removed successfully", "friend_username": username},
            status=status.HTTP_200_OK,
        )


class FriendListViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = FriendListSerializer

    def get_queryset(self):
        return self.request.user.friends.all()


class PostViewSet(mixins.CreateModelMixin, GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer: PostSerializer) -> Post:
        try:
            wall_owner = User.objects.get(username=self.kwargs.get("username"))
        except User.DoesNotExist:
            raise NotFound({"error": "Not Found", "message": "User does not exist"})

        if wall_owner.id != self.request.user.id:
            if not wall_owner.friends.filter(id=self.request.user.id).exists():
                raise PermissionDenied(
                    {"error": "Forbidden", "message": "You do not have permission to perform this action"}
                )

        serializer.save(user=self.request.user, wall_owner=wall_owner)


class RevokeSesionView(APIView):
    def delete(self, request: Request) -> Response:
        Session.objects.filter(user=request.user).delete()

        return Response(
            {"message": "Sessions have been revoked successfully", "username": request.user.username},
            status=status.HTTP_200_OK,
        )
