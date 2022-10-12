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

def home(request):
    to_do_list = ToDoList.objects.order_by('subject_text')[:5]
    output = ', '.join([l.subject_text for l in to_do_list])
    return HttpResponse(output)

def history(request):
    to_do_list = ToDoList.objects.order_by('subject_text')[:5]
    output = ', '.join([l.subject_text for l in to_do_list])
    return HttpResponse("This is history page.")

def detail(request, pk_list, pk_task):
    to_do_list = ToDoList.objects.order_by('subject_text')[:5]
    return HttpResponse(f"This is detail page for task: {pk_task} of list: {pk_list}.")
