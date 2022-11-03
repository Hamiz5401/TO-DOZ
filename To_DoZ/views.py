from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import generic

import datetime
import pytz

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import ToDoList, Task
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me'
]

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'To_DoZ/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

try:
    service = build('classroom', 'v1', credentials=creds)

    # Call the Classroom API
    results = service.courses().list(pageSize=10).execute()
    courses = results.get('courses', [])

    if not courses:
        print('No courses found.')

except HttpError as error:
    print('An error occurred: %s' % error)


def create_classroom_data(user):
    for g_data in courses:
        if not ToDoList.objects.filter(user=user, subject=g_data['name'].replace('/', "-")).exists():
            ToDoList.objects.create(user=user, subject=g_data['name'].replace('/', "-"))
        classwork = service.courses().courseWork().list(courseId=g_data['id']).execute()
        if 'courseWork' in classwork:
            # print(classwork['courseWork'])
            for work in classwork['courseWork']:
                if g_data['id'] != work['courseId']:
                    continue
                submit = service.courses().courseWork().studentSubmissions().list(courseId=g_data['id'],
                                                                                  courseWorkId=work['id']).execute()
                # print("g_data name: ", g_data['name'])
                # print(Task.objects.filter(title=work['title']).exists())
                # print("g_title:", work['title'])
                if not Task.objects.filter(title=work['title']).exists():
                    g_classroom_todo = ToDoList.objects.get(user=user, subject=g_data['name'].replace('/', "-"))
                    # print("g_todo:", g_classroom_todo)
                    duetime = timezone.datetime(work['dueDate']['year'] if 'dueDate' in work else 9999,
                                                work['dueDate']['month'] if 'dueDate' in work else 1,
                                                work['dueDate']['day'] if 'dueDate' in work else 1,
                                                work['dueTime']['hours'] if 'dueTime' in work
                                                                            and 'hours' in work[
                                                                                'dueTime'] else 0,
                                                work['dueTime']['minutes'] if 'dueTime' in work
                                                                              and 'minutes' in work[
                                                                                  'dueTime'] else 0,
                                                tzinfo=pytz.timezone("Asia/Bangkok"))
                    submit_data = submit['studentSubmissions'][0]
                    Task.objects.create(title=work['title'],
                                        detail=work['description'] if 'description' in work else "No description",
                                        deadline=duetime,
                                        status=True if submit_data['state'] == "TURNED_IN"
                                        or submit_data['state'] == "RETURNED" else False,
                                        to_do_list=g_classroom_todo)

@method_decorator(login_required, name="dispatch")
class HomeView(generic.ListView):
    template_name = "To_DoZ/home.html"
    context_object_name = "todolist_list"

    def get_queryset(self):
        user = self.request.user
        if user.socialaccount_set.exists():
            create_classroom_data(user)
        return ToDoList.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


@method_decorator(login_required, name="dispatch")
class HistoryView(generic.ListView):
    template_name = 'To_DoZ/history.html'
    context_object_name = 'todolist_list'

    def get_queryset(self):
        user = self.request.user
        return ToDoList.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class DetailView(generic.DetailView):
    model = Task
    template_name = 'To_DoZ/detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        # context['task'] = self.kwargs['task']
        return context


class TaskCreateView(CreateView):
    model = Task
    template_name = "To_DoZ/task_create_form.html"
    fields = ["title", "detail", "priority", "status", "deadline"]

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")

    def form_valid(self, form):
        form.instance.to_do_list = ToDoList.objects.get(
            pk=self.kwargs["pk_list"])
        return super(TaskCreateView, self).form_valid(form)


class ListCreateView(CreateView):
    model = ToDoList
    template_name = "To_DoZ/list_create_form.html"
    fields = ["subject"]

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ListCreateView, self).form_valid(form)


class TaskUpdateView(UpdateView):
    model = Task
    template_name = "To_DoZ/task_update_form.html"
    fields = ["title", "detail", "priority", "status", "deadline"]

    def get_success_url(self) -> str:
        return reverse("To_DoZ:detail", args=(self.kwargs["pk_list"], self.kwargs["pk"]))


class ListUpdateView(UpdateView):
    model = ToDoList
    template_name = "To_DoZ/list_create_form.html"
    fields = ["subject"]

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")


class TaskDeleteView(DeleteView):
    model = Task
    template_name = "To_DoZ/task_delete_form.html"

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")


class ListDeleteView(DeleteView):
    model = ToDoList
    template_name = "To_DoZ/list_delete_form.html"

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")


@login_required
def done(request, pk_task):
    task_object = Task.objects.get(pk=pk_task)
    if task_object.status:
        task_object.status = False
        task_object.save()
        return HttpResponseRedirect(reverse("To_DoZ:history"))
    task_object.status = True
    task_object.save()
    return HttpResponseRedirect(reverse("To_DoZ:home"))
