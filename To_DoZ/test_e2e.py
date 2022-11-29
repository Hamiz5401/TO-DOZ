from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from decouple import config
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class TestSelenium(StaticLiveServerTestCase):
    """Tests of the Selenium E2E."""

    def setUp(self):
        options = ChromeOptions()
        options.headless = config("HEADLESS", cast=bool, default=True)
        self.browser = Chrome(options=options)
        self.login()
        self.clear_data()

    def login(self):
        username = "test"
        password = "test_todoz"
        url = config("LOGIN_PAGE", cast=str, default="https://todoz-phukit.herokuapp.com/accounts/login/")
        self.browser.get(url)
        if self.browser.current_url == url:
            self.browser.find_element(By.NAME, 'login').send_keys(username)
            self.browser.find_element(By.NAME, 'password').send_keys(password)
            self.browser.find_element(By.CLASS_NAME, 'button__text').click()

    def go_to_home(self):
        self.browser.get(config("HOME_PAGE",cast=str,default="https://todoz-phukit.herokuapp.com/To-Doz/"))

    def go_to_history(self):
        self.browser.get(config("HISTORY_PAGE",cast=str,default="https://todoz-phukit.herokuapp.com/To-Doz/history/"))

    def logout(self):
        self.browser.find_element(By.NAME, 'logout').click()
        self.browser.find_element(By.CLASS_NAME, 'button__text').click()

    def clear_data(self):
        while(self.browser.find_elements(By.PARTIAL_LINK_TEXT, 'DELETE')):
            self.delete_list()

    def create_list(self, subject: str):
        self.browser.find_element(By.CLASS_NAME, 'add_todo_button').click()
        self.browser.find_element(By.NAME, 'subject').send_keys(subject)
        self.browser.find_element(By.CLASS_NAME, 'done_button').click()

    def delete_list(self):
        self.browser.find_element(By.PARTIAL_LINK_TEXT, 'DELETE').click()
        self.browser.find_element(By.CLASS_NAME, 'done_button').click()

    def create_task(self, title: str):
        self.browser.find_element(By.CLASS_NAME, 'add_button').click()
        self.browser.find_element(By.ID, 'id_title').send_keys(title)
        self.browser.find_element(By.CLASS_NAME, 'done_button').click()

    def delete_task(self, name: str):
        self.browser.find_element(By.LINK_TEXT, name).click()
        self.browser.find_element(By.LINK_TEXT, "delete").click()
        self.browser.find_element(By.CLASS_NAME, "done_button").click()
        
    def done_task(self, quantity: int):
        for _ in range(quantity):
            self.browser.find_element(By.CLASS_NAME, 'done_button').click()

    def test_page_title(self):
        url = config("HOME_PAGE", cast=str, default="https://todoz-phukit.herokuapp.com/To-Doz/")
        self.browser.get(url)
        self.assertIn("TO-DOZ", self.browser.title)

    def test_add_list(self):
        self.login()
        n_lists = 5
        detect_list_by = "h3"

        for i in range(1, n_lists):
            self.create_list(f"Test{i}")
            elements = self.browser.find_elements(By.TAG_NAME, detect_list_by)
            self.assertEqual(i, len(elements))

        self.clear_data()

    def test_delete_list(self):
        self.login()
        n_lists = 5
        detect_list_by = "h3"

        for i in range(1, n_lists):
            self.create_list(f"Test{i}")

        for i in range(n_lists-1, 0, -1):
            self.delete_list()
            elements = self.browser.find_elements(By.TAG_NAME, detect_list_by)
            self.assertEqual(i-1, len(elements))

    def test_add_task(self):
        self.login()
        self.create_list('Test1')
        n_tasks = 5
        detect_task_by = "each_task"

        for i in range(1, n_tasks):    
            self.create_task(f"Task{i}")
            elements = self.browser.find_elements(By.CLASS_NAME, detect_task_by)
            self.assertEqual(i, len(elements))

        self.clear_data()

    def test_delete_task(self):
        self.login()
        self.create_list('Test1')
        n_tasks = 5
        detect_task_by = "each_task"

        for i in range(1, n_tasks):
            self.create_task(f"Task{i}")

        for i in range(n_tasks-1, 0, -1):
            self.delete_task(f"Task{i}")
            elements = self.browser.find_elements(By.CLASS_NAME, detect_task_by)
            self.assertEqual(i-1, len(elements))

        self.clear_data()

    def test_done_task(self):
        self.login()
        detect_task_by = "each_task"
        
        # create list
        self.create_list("Test1")

        # create tasks
        n_tasks = 5

        for i in range(1, n_tasks):
            self.create_task(f"Task{i}")
            
        done_tasks = 2
        self.done_task(done_tasks)
        # go to history page
        self.go_to_history()

        # test task
        elements = self.browser.find_elements(By.CLASS_NAME, 'each_task')
        self.assertEqual(done_tasks, len(elements))
        self.clear_data()
