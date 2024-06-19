from django.contrib import admin
from .models import User, Task, Notice, Activity

# Register your models here.
admin.site.register(User)
admin.site.register(Task)
admin.site.register(Notice)
admin.site.register(Activity)
