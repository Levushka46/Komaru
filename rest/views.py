from django.shortcuts import render
from django.db import transaction
from django.db.models import Q
from .serializers import BaseUserSerializer
from .models import User
from rest import exceptions

from rest_framework import serializers
from rest_framework import mixins, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.exceptions import NotFound, ParseError, AuthenticationFailed
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

        access_token = f'Bearer {serializer.validated_data["access"]}'
        return Response(
            {"message": "Logged in successfully", "username": request.data["username"]},
            status=status.HTTP_200_OK,
            headers={"Authorization": access_token},
        )
