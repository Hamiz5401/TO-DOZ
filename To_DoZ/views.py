from __future__ import print_function

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import ToDoList, Task

import os.path


class HomeView(generic.ListView):
    model = ToDoList
    template_name = "To_DoZ/home.html"
    context_object_name = "todolist_list"


class HistoryView(generic.ListView):

    template_name = 'To_DoZ/history.html'
    context_object_name = 'tasks_finished'

    def get_queryset(self):
        return Task.objects.filter(status=True).order_by('-deadline')


class MissingView(generic.ListView):

    template_name = 'To_Doz/missing.html'
    context_object_name = 'tasks_passed_deadline'

    def get_queryset(self):
        return Task.objects.filter(deadline__lte=timezone.localtime()).order_by('-deadline')


def detail(request, pk_list, pk_task):
    to_do_list = ToDoList.objects.order_by('subject_text')[:5]
    return HttpResponse(f"This is detail page for task: {pk_task} of list: {pk_list}.")
