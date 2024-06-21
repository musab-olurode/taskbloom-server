from rest_framework import serializers
from .models import User, Notice, Task, Activity
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from datetime import datetime


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


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "title",
            "role",
            "email",
            "is_active",
        ]

    def to_representation(self, instance: User):
        return {
            "_id": instance.id,
            "id": instance.id,
            "name": instance.name,
            "title": instance.title,
            "role": instance.role,
            "email": instance.email,
            "isActive": instance.is_active,
        }


class UserIdField(serializers.RelatedField):
    def to_internal_value(self, data):
        try:
            user = User.objects.get(id=data)
            return user.id
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with id {data} does not exist")

    def to_representation(self, instance):
        return {
            "_id": instance.id,
            "id": instance.id,
            "name": instance.name,
            "title": instance.title,
            "role": instance.role,
            "email": instance.email,
            "isActive": instance.is_active,
        }


class CreateTaskSerializer(serializers.ModelSerializer):
    team = UserIdField(many=True, queryset=User.objects.all())
    assets = serializers.ListField(child=serializers.URLField())

    class Meta:
        model = Task
        fields = [
            "title",
            "team",
            "date",
            "stage",
            "priority",
            "assets",
        ]

    def to_internal_value(self, data):
        # Convert stage and priority to lowercase
        if "stage" in data:
            data["stage"] = data["stage"].lower()
        if "priority" in data:
            data["priority"] = data["priority"].lower()
        return super().to_internal_value(data)

    def validate(self, attrs):
        team_ids = attrs.get("team")
        for team_id in team_ids:
            if not User.objects.filter(id=team_id).exists():
                raise serializers.ValidationError(
                    f"User with id {team_id} does not exist"
                )
        return attrs

    def create(self, validated_data):
        team_ids = validated_data.pop("team")
        priority = validated_data["priority"]
        date = validated_data["date"]

        request = self.context.get("request")

        formatted_date = date.strftime("%A %B %d, %Y")

        activity_text = "New task has been assigned to you."
        if len(team_ids) > 1:
            activity_text = activity_text + f" and {len(team_ids) - 1} others."

        activity_text = (
            activity_text
            + f" The task priority is set a {priority} priority, so check and act accordingly. The task date is {formatted_date}. Thank you!!!"
        )

        activity = Activity.objects.create(
            type="assigned",
            activity=activity_text,
            by_id=request.user.id,
        )

        task = Task.objects.create(**validated_data)
        task.activities.add(activity)

        notice = Notice.objects.create(
            text=activity_text,
            task=task,
        )

        team = User.objects.filter(id__in=team_ids)
        if team:
            task.team.add(*team)
            notice.team.add(*team)

        return task
