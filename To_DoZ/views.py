from re import T
from django.views.generic.edit import CreateView, UpdateView
from django.views import generic

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import ToDoList, Task

import os.path


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
    

class TaskCreateView(CreateView):
    model = Task
    template_name = "To_DoZ/task_create_form.html"
    fields = ["title", "detail", "priority", "status", "deadline"]

    def get_success_url(self) -> str:
        return reverse("To_DoZ:home")
    
    def form_valid(self, form):
        form.instance.to_do_list = ToDoList.objects.get(pk=self.kwargs["pk_list"])
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
    template_name_suffix = "_update_form"
    fields = ["title", "detail", "priority", "status", "deadline"]

    def get_success_url(self) -> str:
        return reverse("To_DoZ:detail", args=(self.kwargs["pk_list"], self.kwargs["pk"]))


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
