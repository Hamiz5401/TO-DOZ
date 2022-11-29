from django.views.generic.edit import CreateView, UpdateView, DeleteView

import datetime
import pytz
import time

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import ToDoList, Task, Discord_url, Google_token
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from discordwebhook import Discord
from .jobs import add_job, clear_job
from django.utils import timezone
from threading import Thread
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid'
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
        user = self.request.user
        context["user"] = user
        try:
            context["discord"] = Discord_url.objects.get(user=user)
        except:
            context["discord"] = ''

        return context


@method_decorator(login_required, name="dispatch")
class TableView(generic.ListView):
    template_name = "To_DoZ/table.html"
    context_object_name = "task_list"

    def get_queryset(self):
        user = self.request.user
        task = Task.objects.filter(user=user)
        _list = self.request.GET.get('list', '')
        sort_by = self.request.GET.get('sort_by', 'deadline')
        status = self.request.GET.get('status', '')
        priority = self.request.GET.get('priority', '')

        if status:
            if status == 'True':
                task = task.filter(status=True)
            else:
                task = task.filter(status=False)
        if _list:
            task = task.filter(to_do_list=_list)
        if priority:
            task = task.filter(priority=True)

        task = task.order_by(sort_by)

        return task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user
        context["lists"] = ToDoList.objects.filter(user=user)
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


@method_decorator(login_required, name="dispatch")
class DetailView(generic.DetailView):
    model = Task
    template_name = 'To_DoZ/detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@method_decorator(login_required, name="dispatch")
class TaskCreateView(CreateView):
    model = Task
    template_name = "To_DoZ/task_create_form.html"
    fields = ["title", "detail", "priority", "status", "deadline"]

    def get_success_url(self) -> str:
        if Discord_url.objects.filter(user=self.request.user).exists():
            if self.object.deadline != "":
                add_job(self.object, self.request.user)
        return reverse("To_DoZ:home")

    def form_valid(self, form):
        form.instance.to_do_list = ToDoList.objects.get(
            pk=self.kwargs["pk_list"])
        form.instance.user = self.request.user
        return super(TaskCreateView, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
class ListCreateView(CreateView):
    model = ToDoList
    template_name = "To_DoZ/list_create_form.html"
    fields = ["subject"]

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ListCreateView, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
class TaskUpdateView(UpdateView):
    model = Task
    template_name = "To_DoZ/task_update_form.html"
    fields = ["title", "detail", "priority", "status", "deadline"]

    def get_success_url(self) -> str:
        if Discord_url.objects.filter(user=self.request.user).exists():
            if self.object.deadline != "":
                add_job(self.object, self.request.user)
        return reverse("To_DoZ:detail", args=(self.kwargs["pk_list"], self.kwargs["pk"]))


@method_decorator(login_required, name="dispatch")
class ListUpdateView(UpdateView):
    model = ToDoList
    template_name = "To_DoZ/list_create_form.html"
    fields = ["subject"]

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")


@method_decorator(login_required, name="dispatch")
class TaskDeleteView(DeleteView):
    model = Task
    template_name = "To_DoZ/task_delete_form.html"

    def get_success_url(self) -> str:
        if Discord_url.objects.filter(user=self.request.user).exists():
            clear_job(self.object)
        return reverse("To_DoZ:home")


@method_decorator(login_required, name="dispatch")
class ListDeleteView(DeleteView):
    model = ToDoList
    template_name = "To_DoZ/list_delete_form.html"

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")


@method_decorator(login_required, name="dispatch")
class DiscordCreateView(CreateView):
    model = Discord_url
    template_name = "To_DoZ/discord_create_form.html"
    fields = ["url"]

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(DiscordCreateView, self).form_valid(form)


@method_decorator(login_required, name="dispatch")
class DiscordUpdateView(UpdateView):
    model = Discord_url
    template_name = "To_DoZ/discord_update_form.html"
    fields = ["url"]

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
    if not user.socialaccount_set.exists():
        # If user doesn't exists, Return them to Home.
        return HttpResponseRedirect(reverse("To_DoZ:home"))

    creds = None
    if Google_token.objects.filter(user=user).exists():
        g_token = Google_token.objects.get(user=user)
        # get user created token
        creds = Credentials(token=g_token.token,
                            refresh_token=g_token.refresh_token,
                            token_uri=g_token.token_url,
                            client_id=g_token.client_id,
                            client_secret=g_token.client_secret,
                            expiry=g_token.expiry)

    if creds and creds.expiry >= timezone.now() and creds.refresh_token is not None:
        # If credential already exists, Refresh the token.
        creds.refresh(Request())
    # Authorize user by using Google again.
    if not creds and request.GET.get("state", "") == "":
        return redirect_auth(request)

    # Store the Credential.
    if not Google_token.objects.filter(user=user).exists():
        try:
            creds = create_credential(creds, request)
        except:
            return HttpResponseRedirect(reverse("To_DoZ:home"))
        Google_token.objects.create(user=user,
                                    token=creds.token,
                                    refresh_token=creds.refresh_token,
                                    token_url=creds.token_uri,
                                    client_id=creds.client_id,
                                    client_secret=creds.client_secret,
                                    expiry=timezone.datetime.strptime(str(creds.expiry),
                                                                      '%Y-%m-%d %H:%M:%S.%f'))
    # Get data from Google Classroom API.
    # Note: Trick the credential to think that it is not expired.
    creds.expiry = False
    try:
        service = build('classroom', 'v1', credentials=creds)
        results = service.courses().list(pageSize=1, fields="courses(id,name)").execute()
        courses = results.get('courses', [])

        if not courses:
            print('No courses found.')
            return HttpResponseRedirect(reverse("To_DoZ:home"))

        for g_data in courses:
            if not ToDoList.objects.filter(user=user, subject=g_data['name'].replace('/', "-")).exists():
                ToDoList.objects.create(
                    user=user, subject=g_data['name'].replace('/', "-"), classroom_API=True)
            classwork = service.courses().courseWork().list(courseId=g_data['id'],
                                                            fields="courseWork(courseId,id,title,dueDate,dueTime,"
                                                                   "description)").execute()
            if 'courseWork' not in classwork:
                continue

            for work in classwork['courseWork']:
                if g_data['id'] != work['courseId']:
                    continue
                # get user submit data
                submit = service.courses().courseWork().studentSubmissions().list(courseId=g_data['id'],
                                                                                  courseWorkId=work[
                                                                                      'id'],
                                                                                  fields="studentSubmissions("
                                                                                         "state)").execute()
                g_classroom_todo = ToDoList.objects.get(
                    user=user, subject=g_data['name'].replace('/', "-"))
                submit_data = submit['studentSubmissions'][0]
                duetime = create_duetime_google_task(work)
                if Task.objects.filter(title=work['title'],
                                       to_do_list=g_classroom_todo,
                                       user=user).exists():
                    Task.objects.filter(to_do_list=g_classroom_todo, title=work['title'], user=user).update(
                        title=work['title'],
                        detail=work['description'] if 'description' in work else "No description",
                        deadline=duetime,
                        status=True if submit_data['state'] == "TURNED_IN"
                                       or submit_data['state'] == "RETURNED" else False, )
                    if Discord_url.objects.filter(user=user).exists():
                        add_job(Task.objects.get(to_do_list=g_classroom_todo, title=work['title'], user=user),
                                user)
                else:
                    Task.objects.create(title=work['title'],
                                        detail=work[
                                            'description'] if 'description' in work else "No description",
                                        deadline=duetime,
                                        status=True if submit_data['state'] == "TURNED_IN"
                                                       or submit_data['state'] == "RETURNED" else False,
                                        to_do_list=g_classroom_todo,
                                        user=user)
                    if Discord_url.objects.filter(user=user).exists():
                        add_job(Task.objects.get(to_do_list=g_classroom_todo, title=work['title'], user=user),
                                user)
        if Discord_url.objects.filter(user=user).exists():
            dis = Discord_url.objects.filter(user=user)
            dis_url = dis[0]
            discord = Discord(url=dis_url)
            discord.post(
                content=f"{user} has update google classroom data.")
    except HttpError as error:
        print('An error occurred: %s' % error)
    return HttpResponseRedirect(reverse("To_DoZ:home"))


def create_duetime_google_task(work):
    if 'dueDate' not in work or 'dueTime' not in work:
        return None
    due_hrs = 0
    due_mins = 0
    if 'dueTime' in work:
        dueTime = work['dueTime']
        if 'hours' in dueTime:
            due_hrs = dueTime['hours']
        if 'minutes' in dueTime:
            due_mins = dueTime['minutes']
    return datetime.datetime(year=work['dueDate']['year'],
                             month=work['dueDate']['month'],
                             day=work['dueDate']['day'],
                             hour=due_hrs,
                             minute=due_mins,
                             tzinfo=pytz.timezone("UTC"))


def redirect_auth(request):
    flow = InstalledAppFlow.from_client_secrets_file(
        'To_DoZ/credentials.json', SCOPES, redirect_uri="http://127.0.0.1:8000/To-Doz/get_classroom_data")
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true',
                                                      prompt='consent')
    request.session['state'] = state
    # redirect user
    return HttpResponseRedirect(authorization_url)


def create_credential(creds, request):
    flow = InstalledAppFlow.from_client_secrets_file(
        'To_DoZ/credentials.json', SCOPES, redirect_uri="http://127.0.0.1:8000/To-Doz/get_classroom_data",
        state=request.GET.get("state", ""))
    authorization_response = request.build_absolute_uri()
    # Note: Make it think that it always connected to https
    if authorization_response[0:7] == "http://":
        authorization_response = "https://" + authorization_response[7:]
    flow.fetch_token(authorization_response=authorization_response)
    creds = flow.credentials
    return creds
