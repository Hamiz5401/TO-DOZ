from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from To_DoZ import views
from To_DoZ.models import Task, ToDoList, User


# TODO test done
# todo test get_success_url
# todo test done

class QuestionModelTests(TestCase):

    def test_is_late(self):
        task = Task(deadline=timezone.now() + timezone.timedelta(-1))
        self.assertTrue(task.is_late())


class HomeViewTests(TestCase):
    def test_no_list(self):
        response = self.client.get(reverse('To_DoZ:home'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.context, None)


# class test(TestCase):
#     def test(self):
#         User.objects.create(username='test1', password='1234')
#         ToDoList.objects.create(subject='subtest1',user=User.objects.get(pk=1))
#         Task.objects.create(title='work1',detail='todo1',to_do_list=ToDoList.objects.get(pk=1))
#         response = self.client.get(reverse('To_DoZ:done'))
#         views.done(response,1)
#         self.assertTrue(Task.objects.get(pk=1).status)
