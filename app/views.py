# views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Notice, Task, Activity
from .serializers import (
    UserRegisterSerializer,
    LoginSerializer,
    UserSerializer,
    NoticeSerializer,
    CreateTaskSerializer,
    TeamSerializer,
)
from .utils import create_jwt_token
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Count
from rest_framework.authtoken.models import Token

User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    user = request.data
    serializer = UserRegisterSerializer(data=user)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        user_data = serializer.data
        response = Response(
            user_data,
            status=status.HTTP_201_CREATED,
        )
        if user_data["isAdmin"]:
            create_jwt_token(response, user_data["id"])
        return response
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    data = request.data
    serializer = LoginSerializer(data=data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    user_data = serializer.data
    create_jwt_token(response, user_data["id"])
    return response


@api_view(["POST"])
def logout_user(request):
    response = Response(
        {"message": "Logged out successfully"}, status=status.HTTP_200_OK
    )
    response.delete_cookie("token")
    Token.objects.filter(key=request.COOKIES.get("token")).delete()
    return response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_team_list(request):
    search = request.query_params.get("search", None)
    query = {}
    if search:
        query = {
            "name__icontains": search,
            "title__icontains": search,
            "role__icontains": search,
            "email__icontains": search,
        }
    users = User.objects.filter(**query)
    serializer = TeamSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_notifications_list(request):
    user = request.user
    notices = (
        # Notice.objects.filter(team=user, is_read__nin=[user.id])
        Notice.objects.filter(team=user)
        .exclude(is_read__in=[user.id])
        .select_related("task")
        .order_by("-id")
    )
    serializer = NoticeSerializer(notices, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def mark_notification_read(request):
    user = request.user
    is_read_type = request.query_params.get("isReadType")
    notice_id = request.query_params.get("id")

    if is_read_type == "all":
        notices = Notice.objects.filter(team=user).exclude(is_read__in=[user.id])
        for notice in notices:
            notice.is_read.add(user)
            notice.save()
    else:
        Notice.objects.filter(id=notice_id).exclude(is_read__in=[user.id]).update(
            is_read=[user.id]
        )

    return Response({"status": True, "message": "Done"}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    data = request.data

    try:
        user = User.objects.get(id=data.get("id"))
    except User.DoesNotExist:
        return Response(
            {"status": False, "message": "User not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    user.name = data.get("name", user.name)
    user.title = data.get("title", user.title)
    user.role = data.get("role", user.role)
    user.save()
    user.password = None
    serializer = UserSerializer(user)
    return Response(
        {
            "status": True,
            "message": "Profile Updated Successfully.",
            "user": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def activate_or_delete_user_profile(request, id):
    if request.method == "GET":
        try:
            user = User.objects.get(id=id)
            user.is_active = request.data["isActive"]
            user.save()
            user.password = None
            return Response(
                {
                    "status": True,
                    "message": f'User account has been {"activated" if user.is_active else "disabled"}',
                },
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        if not request.user.is_superuser:
            return Response(
                {"status": False, "message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(id=id)
            user.delete()
            return Response(
                {"status": True, "message": "User deleted successfully"},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"status": False, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def change_user_password(request):
    user = request.user
    if user.id == "65ff94c7bb2de638d0c73f63":
        return Response(
            {
                "status": False,
                "message": "This is a test user. You cannot change the password. Thank you!!!",
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    user.set_password(request.data["password"])
    user.save()
    user.password = None
    return Response(
        {"status": True, "message": "Password changed successfully."},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def create_task(request):
    data = request.data
    serializer = CreateTaskSerializer(data=data, context={"request": request})
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        task_data = serializer.data
        return Response(
            {
                "status": True,
                "task": task_data,
                "message": "Task created successfully.",
            },
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def duplicate_task(request, id):
    try:
        user_id = request.user.id
        task = Task.objects.get(id=id)

        team_count = task.team.count()

        text = "New task has been assigned to you"
        if team_count > 1:
            text = text + f" and {team_count - 1} others."

        text = (
            text
            + f" The task priority is set a {task.priority} priority, so check and act accordingly. The task date is {task.date.strftime('%A %B %d, %Y')}. Thank you!!!"
        )

        activity = Activity.objects.create(
            type="assigned",
            activity=text,
            by_id=user_id,
        )

        new_task = Task.objects.create(
            title="Duplicate - " + task.title,
            stage=task.stage,
            date=task.date,
            priority=task.priority,
            assets=task.assets,
        )
        new_task.activities.add(activity)
        new_task.team.set(task.team.all())

        notice = Notice.objects.create(
            text=text,
            task=new_task,
        )
        notice.team.set(task.team.all())

        return Response(
            {"status": True, "message": "Task duplicated successfully."},
            status=status.HTTP_200_OK,
        )
    except ObjectDoesNotExist:
        return Response(
            {"status": False, "message": "Task not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        print(e)
        return Response(
            {"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_task(request, id):
    try:
        title = request.data.get("title")
        date = request.data.get("date")
        team = request.data.get("team")
        stage = request.data.get("stage").lower()
        priority = request.data.get("priority").lower()
        assets = request.data.get("assets")

        task = Task.objects.get(id=id)

        task.title = title
        task.date = date
        task.priority = priority
        task.assets = assets
        task.stage = stage

        task.save()
        task.team.set(team)

        return Response(
            {"status": True, "message": "Task updated successfully."},
            status=status.HTTP_200_OK,
        )
    except ObjectDoesNotExist:
        return Response(
            {"status": False, "message": "Task not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        print(e)
        return Response(
            {"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_task_stage(request, id):
    try:
        stage = request.data.get("stage").lower()

        task = Task.objects.get(id=id)

        task.stage = stage

        task.save()

        return Response(
            {"status": True, "message": "Task stage changed successfully."},
            status=status.HTTP_200_OK,
        )
    except ObjectDoesNotExist:
        return Response(
            {"status": False, "message": "Task not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        print(e)
        return Response(
            {"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def create_subtask(request, id):
    try:
        title = request.data.get("title")
        tag = request.data.get("tag")
        date = request.data.get("date")

        new_sub_task = {
            "title": title,
            "date": date,
            "tag": tag,
        }

        task = Task.objects.get(id=id)

        task.sub_tasks.append(new_sub_task)

        task.save()

        return Response(
            {"status": True, "message": "SubTask added successfully."},
            status=status.HTTP_200_OK,
        )
    except ObjectDoesNotExist:
        return Response(
            {"status": False, "message": "Task not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        print(e)
        return Response(
            {"status": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_tasks(request):
    user_id = request.user.id
    is_admin = request.user.is_superuser
    stage = request.GET.get("stage")
    is_trashed = request.GET.get("isTrashed") == "true"
    search = request.GET.get("search")

    query = Q(is_trashed=is_trashed)

    if not is_admin:
        query &= Q(team__in=[user_id])
    if stage:
        query &= Q(stage=stage)

    if search:
        search_query = (
            Q(title__icontains=search)
            | Q(stage__icontains=search)
            | Q(priority__icontains=search)
        )
        query &= search_query

    tasks = Task.objects.filter(query).order_by("-id")

    tasks_data = [
        {
            "id": task.id,
            "_id": task.id,
            "title": task.title,
            "stage": task.stage,
            "priority": task.priority,
            "subTasks": task.sub_tasks,
            "assets": task.assets,
            "date": task.date.strftime("%Y-%m-%d"),
            "team": [
                {
                    "id": member.id,
                    "_id": member.id,
                    "name": member.name,
                    "title": member.title,
                    "role": member.role,
                    "email": member.email,
                }
                for member in task.team.all()
            ],
            "activities": [
                {
                    "id": activity.id,
                    "_id": activity.id,
                    "type": activity.type,
                    "activity": activity.activity,
                    "by": activity.by.name,
                    "date": activity.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for activity in task.activities.all()
            ],
        }
        for task in tasks
    ]

    return Response({"status": True, "tasks": tasks_data}, status=status.HTTP_200_OK)


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def get_or_trash_task(request, id):
    if request.method == "GET":
        try:
            task = Task.objects.get(id=id)

            task_data = {
                "id": task.id,
                "_id": task.id,
                "title": task.title,
                "stage": task.stage,
                "priority": task.priority,
                "subTasks": task.sub_tasks,
                "assets": task.assets,
                "date": task.date.strftime("%Y-%m-%d"),
                "team": [
                    {
                        "id": member.id,
                        "_id": member.id,
                        "name": member.name,
                        "title": member.title,
                        "role": member.role,
                        "email": member.email,
                    }
                    for member in task.team.all()
                ],
                "activities": [
                    {
                        "id": activity.id,
                        "_id": activity.id,
                        "type": activity.type,
                        "activity": activity.activity,
                        "by": activity.by.name,
                    }
                    for activity in task.activities.all()
                ],
            }

            return Response(
                {"status": True, "task": task_data}, status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {"status": False, "message": "Task not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
    else:
        if not request.user.is_superuser:
            return Response(
                {"status": False, "message": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            task = Task.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response(
                {"status": False, "message": "Task not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        task.is_trashed = True

        task.save()

        return Response(
            {"status": True, "message": "Task trashed successfully."},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_task_activity(request, id):
    user_id = request.user.id
    type = request.data.get("type")
    activity = request.data.get("activity")

    try:
        task = Task.objects.get(id=id)

        new_activity = Activity.objects.create(
            type=type, activity=activity, by_id=user_id
        )

        task.activities.add(new_activity)

        task.save()

        return Response(
            {"status": True, "message": "Activity posted successfully."},
            status=status.HTTP_200_OK,
        )
    except ObjectDoesNotExist:
        return Response(
            {"status": False, "message": "Task not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_restore_task(request, id):
    action_type = request.GET.get("actionType")

    try:
        if action_type == "delete":
            Task.objects.get(id=id).delete()
        elif action_type == "deleteAll":
            Task.objects.filter(is_trashed=True).delete()
        elif action_type == "restore":
            task = Task.objects.get(id=id)
            task.is_trashed = False
            task.save()
        elif action_type == "restoreAll":
            Task.objects.filter(is_trashed=True).update(is_trashed=False)

        return Response(
            {"status": True, "message": "Operation performed successfully."},
            status=status.HTTP_200_OK,
        )
    except ObjectDoesNotExist:
        return Response(
            {"status": False, "message": "Task not found"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_statistics(request):
    user_id = request.user.id
    is_admin = request.user.is_superuser

    try:
        if is_admin:
            all_tasks = Task.objects.filter(is_trashed=False).order_by("-id")
        else:
            all_tasks = Task.objects.filter(
                is_trashed=False, team__id=user_id
            ).order_by("-id")

        users = User.objects.filter(is_active=True).values(
            "name", "title", "role", "is_active", "created_at"
        )[:10]

        raw_grouped_tasks = (
            all_tasks.values("stage").annotate(count=Count("stage")).order_by("stage")
        )
        grouped_tasks = {task["stage"]: task["count"] for task in raw_grouped_tasks}

        raw_graph_data = (
            all_tasks.values("priority")
            .annotate(total=Count("priority"))
            .order_by("priority")
        )
        graph_data = [
            {"name": data["priority"], "total": data["total"]}
            for data in raw_graph_data
        ]

        total_tasks = all_tasks.count()
        last_10_tasks = all_tasks[:10]

        last_10_tasks_data = [
            {
                "id": task.id,
                "_id": task.id,
                "title": task.title,
                "stage": task.stage,
                "priority": task.priority,
                "subTasks": task.sub_tasks,
                "assets": task.assets,
                "date": task.date.strftime("%Y-%m-%d"),
                "team": [
                    {
                        "id": member.id,
                        "_id": member.id,
                        "name": member.name,
                        "title": member.title,
                        "role": member.role,
                        "email": member.email,
                    }
                    for member in task.team.all()
                ],
                "activities": [
                    {
                        "id": activity.id,
                        "_id": activity.id,
                        "type": activity.type,
                        "activity": activity.activity,
                        "by": activity.by.name,
                        "date": activity.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    for activity in task.activities.all()
                ],
            }
            for task in last_10_tasks
        ]

        users_data = [
            {
                "name": user["name"],
                "title": user["title"],
                "role": user["role"],
                "isActive": user["is_active"],
                "createdAt": user["created_at"],
            }
            for user in users
        ]

        summary = {
            "totalTasks": total_tasks,
            "last10Task": last_10_tasks_data,
            "users": users_data if is_admin else [],
            "tasks": grouped_tasks,
            "graphData": graph_data,
        }

        return Response(
            {"status": True, **summary, "message": "Successfully."},
            status=status.HTTP_200_OK,
        )
    except Exception as error:
        return Response(
            {"status": False, "message": str(error)}, status=status.HTTP_400_BAD_REQUEST
        )
