from django.http import HttpResponseRedirect

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import views
from .models import Task, ToDoList, User


class QuestionModelTests(TestCase):

    def test_is_late(self):
        task = Task(deadline=timezone.now() + timezone.timedelta(-1))
        self.assertTrue(task.is_late())


class HomeViewTests(TestCase):
    def test_no_list(self):
        response = self.client.get(reverse('To_DoZ:home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.context, None)


class Donetest(TestCase):
    def test_done(self):
        User.objects.create(username='test1', password='1234')
        ToDoList.objects.create(subject='subtest1', user=User.objects.get(pk=1))
        Task.objects.create(title='work1', detail='todo1', to_do_list=ToDoList.objects.get(pk=1))
        # response = self.client.get(reverse('To_DoZ:done',args=[1]))
        views.done(ToDoList.objects.get(pk=1), 1)
        self.assertTrue(Task.objects.get(pk=1).status)
        views.done(ToDoList.objects.get(pk=1), 1)
        self.assertFalse(Task.objects.get(pk=1).status)


class ClassroomTest(TestCase):
    def test_user(self):
        User.objects.create(username='test1', password='1234')
        ToDoList.objects.create(subject='subtest1', user=User.objects.get(pk=1))
        self.assertEqual(type(views.create_classroom_data(ToDoList.objects.get(pk=1))),
                         type(HttpResponseRedirect(reverse("To_DoZ:home"))))

    def test_user_social(self):
        User.objects.create(username='test1', password='1234')
        ToDoList.objects.create(subject='subtest1', user=User.objects.get(pk=1))
