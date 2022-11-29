from django.contrib import admin

# Register your models here.
from .models import ToDoList, Task, Discord_url, Google_token
admin.site.register(ToDoList)
admin.site.register(Task)
admin.site.register(Discord_url)
admin.site.register(Google_token)
