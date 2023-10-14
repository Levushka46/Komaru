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
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.decorators import action
from rest_framework.response import Response


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = BaseUserSerializer
    queryset = User.objects.all()

    @action(detail=False, methods=["post"])
    def register(self, request):
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
