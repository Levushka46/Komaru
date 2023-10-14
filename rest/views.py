from django.shortcuts import render
from django.db import transaction
from .serializers import BaseUserSerializer
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework.exceptions import NotFound


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):

    def get_serializer_class(self):
        return BaseUserSerializer
