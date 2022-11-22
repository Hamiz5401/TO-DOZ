from django.http import HttpResponseRedirect

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import views
from .models import Task, ToDoList, User

from selenium import webdriver
from selenium.webdriver.common.by import By


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


class TestSelenium(TestCase):
    """Tests of the Selenium E2E."""

    def setUp(self):

        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)

    def test_page_access(self):
        url = "https://todoz-phukit.herokuapp.com/To-Doz/"
        self.browser.get(url)
        self.assertNotEqual(url, self.browser.current_url)
        url = "https://todoz-phukit.herokuapp.com/accounts/login/"
        self.browser.get(url)
        self.assertEqual(url, self.browser.current_url)

    def test_page_title(self):
        url = "https://todoz-phukit.herokuapp.com/To-Doz/"
        self.browser.get(url)
        self.assertIn("TO-DOZ", self.browser.title)

    def test_login(self):
        user = "test"
        password = "test_todoz"
        url = "https://todoz-phukit.herokuapp.com/accounts/login/"
        self.browser.get(url)
        self.browser.find_element(By.NAME, 'login').send_keys(user)
        self.browser.find_element(By.NAME, 'password').send_keys(password)
        self.browser.find_element(By.CLASS_NAME, 'button__text').click()
        self.assertNotEqual(url, self.browser.current_url)

    def test_add_list(self):
        user = "test"
        password = "test_todoz"
        url = "https://todoz-phukit.herokuapp.com/accounts/login/"
        self.browser.get(url)
        self.browser.find_element(By.NAME, 'login').send_keys(user)
        self.browser.find_element(By.NAME, 'password').send_keys(password)
        self.browser.find_element(By.CLASS_NAME, 'button__text').click()
        
        self.browser.find_element(By.CLASS_NAME, 'add_todo_button').click()
        to_do_list = "Test1"
        self.browser.find_element(By.NAME, 'subject').send_keys(to_do_list)
        self.browser.find_element(By.CLASS_NAME, 'done_button').click()
        
        home = "https://todoz-phukit.herokuapp.com/To-Doz/"
        self.assertEqual(home, self.browser.current_url)

        elements = self.browser.find_elements(By.TAG_NAME, 'h3')
        self.assertEqual(1, len(elements))
        
        self.browser.find_element(By.PARTIAL_LINK_TEXT, 'DELETE').click()
        self.browser.find_element(By.CLASS_NAME, 'done_button').click()
        
        elements = self.browser.find_elements(By.TAG_NAME, 'h3')
        self.assertEqual(0, len(elements))
