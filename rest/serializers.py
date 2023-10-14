from rest_framework.serializers import Serializer, CharField, ModelSerializer, IntegerField
from rest_framework import serializers
from .models import User


class BaseUserSerializer(ModelSerializer):
    
    def create(self, validated_data):
        user = User.objects.create_user(
            **validated_data
        )
        return user

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        read_only_fields = ['id']
        extra_kwargs = {'password': {'write_only': True,
                                     'style': {'input_type': 'password'}}, }
