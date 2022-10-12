from django.contrib import admin

# Register your models here.
from .models import ToDoList, Task
admin.site.register(ToDoList)
admin.site.register(Task)