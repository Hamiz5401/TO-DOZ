from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# Create your models here.
class ToDoList(models.Model):
    """List Model."""
    subject = models.CharField(max_length=200)
    classroom_API = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"List: {self.subject}."
        # return f"List: {self.subject_text} of User: {self.user.USERNAME_FIELD}."


class Task(models.Model):
    title = models.CharField(max_length=200)
    detail = models.CharField(max_length=1000, null=True, blank=True)
    priority = models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    deadline = models.DateTimeField(null=True, blank=True)
    to_do_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def is_late(self):
        return timezone.localtime() > self.deadline

    def __str__(self):
        return f"Task: {self.title}."


class Discord_url(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.url}"


class Google_token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500)
    token_url = models.CharField(max_length=500)
    client_id = models.CharField(max_length=500)
    client_secret = models.CharField(max_length=500)
    expiry = models.CharField(max_length=500)
