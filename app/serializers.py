from rest_framework import serializers
from .models import User, Notice, Task
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


def snake_to_camel(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class CamelCaseSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {snake_to_camel(key): value for key, value in rep.items()}


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "title",
            "role",
            "email",
            "is_active",
            "is_superuser",
            "password",
        ]

    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data["name"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_superuser=validated_data.get("is_superuser", False),
            role=validated_data["role"],
            title=validated_data["title"],
        )
        return user

    def to_representation(self, instance):
        return {
            "_id": instance.id,
            "id": instance.id,
            "name": instance.name,
            "title": instance.title,
            "role": instance.role,
            "email": instance.email,
            "isActive": instance.is_active,
            "isAdmin": instance.is_superuser,
        }


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        request = self.context.get("request")
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("invalid email or password")
        if not user.is_active:
            raise AuthenticationFailed(
                "user account has been deactivated, contact the administrator"
            )
        return user

    def to_representation(self, instance):
        return {
            "_id": instance.id,
            "id": instance.id,
            "name": instance.name,
            "title": instance.title,
            "role": instance.role,
            "email": instance.email,
            "isActive": instance.is_active,
            "isAdmin": instance.is_superuser,
        }


class UserSerializer(CamelCaseSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "title", "role", "email", "is_active", "is_superuser"]

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "title": instance.title,
            "role": instance.role,
            "email": instance.email,
            "isActive": instance.is_active,
            "isAdmin": instance.is_superuser,
        }


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "title", "role", "email", "is_active", "is_superuser"]


class NoticeSerializer(CamelCaseSerializer):
    class Meta:
        model = Notice
        fields = "__all__"


class TaskSerializer(CamelCaseSerializer):
    class Meta:
        model = Task
        fields = "__all__"
