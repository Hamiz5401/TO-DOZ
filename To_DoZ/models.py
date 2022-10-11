from django.db import models
from django.contrib.auth.models import User


# Create your models here.


class ToDoList(models.Model):
    """List Model."""
    subject_text = models.CharField(max_length=200)
    classroom_API = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)



class History(models.Model):
    to_do_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE)


class Task(models.Model):
    title = models.CharField(max_length=200)
    detail = models.CharField(max_length=1000)
    priority = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    deadline = models.DateTimeField(null=True, blank=True)
    to_do_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE)

