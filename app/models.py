from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager
from django.conf import settings
import uuid


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    tasks = models.ManyToManyField("Task", blank=True, related_name="assigned_users")
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "title", "role"]

    def __str__(self):
        return self.email


class Activity(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(
        max_length=15,
        choices=[
            ("assigned", "Assigned"),
            ("started", "Started"),
            ("in_progress", "In Progress"),
            ("bug", "Bug"),
            ("completed", "Completed"),
            ("commented", "Commented"),
        ],
        default="assigned",
    )
    activity = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activities"
    )

    def __str__(self):
        return self.activity


class Task(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    priority = models.CharField(
        max_length=10,
        choices=[
            ("high", "High"),
            ("medium", "Medium"),
            ("normal", "Normal"),
            ("low", "Low"),
        ],
        default="normal",
    )
    stage = models.CharField(
        max_length=15,
        choices=[
            ("todo", "To Do"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
        ],
        default="todo",
    )
    activities = models.ManyToManyField(Activity, blank=True)
    sub_tasks = models.JSONField(default=list, blank=True)
    assets = models.JSONField(default=list, blank=True)
    team = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="team_tasks", blank=True
    )
    is_trashed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Notice(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="notices")
    text = models.TextField()
    task = models.ForeignKey("Task", on_delete=models.CASCADE, related_name="notices")
    noti_type = models.CharField(
        max_length=10,
        choices=[
            ("alert", "Alert"),
            ("message", "Message"),
        ],
        default="alert",
    )
    is_read = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="read_notices", blank=True
    )

    def __str__(self):
        return self.text[:50]
