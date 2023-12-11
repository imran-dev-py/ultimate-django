from rest_framework import serializers

from djoser.serializers import (
	UserCreateSerializer as BaseUserCreateSerializer,
	UserSerializer as BaseUserSerializer
)


class UserCreateSerializer(BaseUserCreateSerializer):
	class Meta(BaseUserCreateSerializer.Meta):
		fields = ["id", "username", "password", "email", "first_name", "last_name"]
		read_only_fields = ["id"]


class UserSerializer(BaseUserSerializer):
	class Meta(BaseUserSerializer.Meta):
		fields = ["id", "username", "first_name", "last_name", "email"]
		read_only_fields = fields