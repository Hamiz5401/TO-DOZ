from django.views.generic.edit import CreateView, UpdateView, DeleteView

import datetime
import pytz

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import ToDoList, Task, Discord_url
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from discordwebhook import Discord
from .jobs import add_job, clear_job

import os.path

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me'
]


@method_decorator(login_required, name="dispatch")
class HomeView(generic.ListView):
    template_name = "To_DoZ/home.html"
    context_object_name = "todolist_list"

    def get_queryset(self):
        user = self.request.user
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
        return context


class TaskCreateView(CreateView):
    model = Task
    template_name = "To_DoZ/task_create_form.html"
    fields = ["title", "detail", "priority", "status", "deadline"]

    def get_success_url(self) -> str:
        add_job(self.object, self.request.user)
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
        add_job(self.object, self.request.user)
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
        clear_job(self.object)
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


def create_classroom_data(request):
    user = request.user
    if user.socialaccount_set.exists():

        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'To_DoZ/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('classroom', 'v1', credentials=creds)

            results = service.courses().list(pageSize=1).execute()
            courses = results.get('courses', [])

            if not courses:
                print('No courses found.')

            for g_data in courses:
                if not ToDoList.objects.filter(user=user, subject=g_data['name'].replace('/', "-")).exists():
                    ToDoList.objects.create(user=user, subject=g_data['name'].replace('/', "-"))
                classwork = service.courses().courseWork().list(courseId=g_data['id']).execute()
                if 'courseWork' in classwork:
                    for work in classwork['courseWork']:
                        if g_data['id'] != work['courseId']:
                            continue
                        submit = service.courses().courseWork().studentSubmissions().list(courseId=g_data['id'],
                                                                                          courseWorkId=work[
                                                                                              'id']).execute()
                        g_classroom_todo = ToDoList.objects.get(user=user, subject=g_data['name'].replace('/', "-"))
                        if not Task.objects.filter(title=work['title']).exists():
                            print("g_todo:", g_classroom_todo)
                            duetime = datetime.datetime(year=work['dueDate']['year'] if 'dueDate' in work else 9999,
                                                        month=work['dueDate']['month'] if 'dueDate' in work else 1,
                                                        day=work['dueDate']['day'] if 'dueDate' in work else 1,
                                                        hour=(work['dueTime']['hours']) if 'dueTime' in work
                                                                                           and 'hours' in work[
                                                                                               'dueTime'] else 0,
                                                        minute=work['dueTime']['minutes'] if 'dueTime' in work
                                                                                             and 'minutes' in work[
                                                                                                 'dueTime'] else 0,
                                                        tzinfo=pytz.timezone("UTC"))
                            submit_data = submit['studentSubmissions'][0]
                            Task.objects.create(title=work['title'],
                                                detail=work[
                                                    'description'] if 'description' in work else "No description",
                                                deadline=duetime,
                                                status=True if submit_data['state'] == "TURNED_IN"
                                                               or submit_data['state'] == "RETURNED" else False,
                                                to_do_list=g_classroom_todo)
                            add_job(Task.objects.get(to_do_list=g_classroom_todo, title=work['title']))
            if Discord_url.objects.filter(user=user).exists():
                dis = Discord_url.objects.filter(user=user)
                dis_url = dis[0]
                discord = Discord(url=dis_url)
                discord.post(content=f"{user} has update google classroom data.")

        except HttpError as error:
            print('An error occurred: %s' % error)
        return HttpResponseRedirect(reverse("To_DoZ:home"))
    else:
        return HttpResponseRedirect(reverse("To_DoZ:home"))
