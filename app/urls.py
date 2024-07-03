from django.urls import path
from .views import (
    register_user,
    login_user,
    logout_user,
    get_team_list,
    get_notifications_list,
    mark_notification_read,
    update_user_profile,
    activate_or_delete_user_profile,
    change_user_password,
    # Task
    create_task,
    duplicate_task,
    post_task_activity,
    dashboard_statistics,
    get_tasks,
    get_or_trash_task,
    create_subtask,
    update_task,
    update_task_stage,
    delete_restore_task,
    delete_restore_all_tasks,
)

urlpatterns = [
    # Users
    path("user/register", register_user, name="register_user"),
    path("user/login", login_user, name="login_user"),
    path("user/logout", logout_user, name="logout_user"),
    path("user/get-team", get_team_list, name="get_team_list"),
    path("user/notifications", get_notifications_list, name="get_notifications_list"),
    path("user/read-noti", mark_notification_read, name="mark_notification_read"),
    path("user/profile", update_user_profile, name="update_user_profile"),
    path("user/change-password", change_user_password, name="change_user_password"),
    path(
        "user/<uuid:id>",
        activate_or_delete_user_profile,
        name="activate_or_delete_user_profile",
    ),
    # Tasks
    path("task/create", create_task, name="create_task"),
    path("task/duplicate/<uuid:id>", duplicate_task, name="duplicate_task"),
    path("task/activity/<uuid:id>", post_task_activity, name="post_task_activity"),
    path("task/dashboard", dashboard_statistics, name="dashboard_statistics"),
    path("task", get_tasks, name="get_tasks"),
    path("task/<uuid:id>", get_or_trash_task, name="get_or_trash_task"),
    path("task/create-subtask/<uuid:id>", create_subtask, name="create_subtask"),
    path("task/update/<uuid:id>", update_task, name="update_task"),
    path("task/change-stage/<uuid:id>", update_task_stage, name="update_task_stage"),
    path(
        "task/delete-restore/<uuid:id>",
        delete_restore_task,
        name="delete_restore_task",
    ),
    path(
        "task/delete-restore", delete_restore_all_tasks, name="delete_restore_all_tasks"
    ),
]
