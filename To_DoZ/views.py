from django.views.generic.edit import CreateView, UpdateView, DeleteView

import datetime
import pytz

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
        Task.objects.filter(deadline=None).update(
            deadline=timezone.datetime(year=9999, month=1, day=1, hour=0, minute=0))
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
        context["user"] = self.request.user
        context["lists"] = ToDoList.objects.all()
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
        form.instance.to_do_list = ToDoList.objects.get(pk=self.kwargs["pk_list"])
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
    if user.socialaccount_set.exists():

        creds = None
        if Google_token.objects.filter(user=user).exists():
            g_token = Google_token.objects.get(user=user)
            creds = Credentials(token=g_token.token,
                                refresh_token=g_token.refresh_token,
                                token_uri=g_token.token_url,
                                client_id=g_token.client_id,
                                client_secret=g_token.client_secret,
                                expiry=g_token.expiry)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'To_DoZ/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            Google_token.objects.create(user=user,
                                        token=creds.token,
                                        refresh_token=creds.refresh_token,
                                        token_url=creds.token_uri,
                                        client_id=creds.client_id,
                                        client_secret=creds.client_secret,
                                        expiry=datetime.datetime.strptime(str(creds.expiry), '%Y-%m-%d %H:%M:%S.%f'))
        try:
            service = build('classroom', 'v1', credentials=creds)

            results = service.courses().list(pageSize=10).execute()
            courses = results.get('courses', [])

            if not courses:
                print('No courses found.')

            for g_data in courses:
                if not ToDoList.objects.filter(user=user, subject=g_data['name'].replace('/', "-")).exists():
                    ToDoList.objects.create(
                        user=user, subject=g_data['name'].replace('/', "-"), classroom_API=True)
                classwork = service.courses().courseWork().list(
                    courseId=g_data['id']).execute()
                if 'courseWork' in classwork:
                    for work in classwork['courseWork']:
                        if g_data['id'] != work['courseId']:
                            continue
                        submit = service.courses().courseWork().studentSubmissions().list(courseId=g_data['id'],
                                                                                          courseWorkId=work[
                                                                                              'id']).execute()
                        g_classroom_todo = ToDoList.objects.get(
                            user=user, subject=g_data['name'].replace('/', "-"))
                        submit_data = submit['studentSubmissions'][0]
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
                discord.post(content=f"{user} has update google classroom data.")
        except HttpError as error:
            print('An error occurred: %s' % error)
        return HttpResponseRedirect(reverse("To_DoZ:home"))
    else:
        return HttpResponseRedirect(reverse("To_DoZ:home"))
