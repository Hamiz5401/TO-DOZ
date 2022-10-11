from __future__ import print_function

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import os.path

def home(request):
    return HttpResponse("This is home page.")

def history(request):
    return HttpResponse("This is history page.")

def detail(request, pk_list, pk_task):
    return HttpResponse(f"This is detail page for task: {pk_task} of list: {pk_list}.")