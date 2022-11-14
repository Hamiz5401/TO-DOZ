[![codecov](https://codecov.io/gh/Hamiz5401/TO-DOZ/branch/main/graph/badge.svg?token=4CJU7ZB2JC)](https://codecov.io/gh/Hamiz5401/TO-DOZ)
[![Test with unittest](https://github.com/Hamiz5401/TO-DOZ/actions/workflows/unittest-test.yml/badge.svg)](https://github.com/Hamiz5401/TO-DOZ/actions/workflows/unittest-test.yml)
# TO-DOZ
To-DoZ is a web application that lets students create their own to-do list and to-do list  according to the class that they enrolled in the google classroom.
This app provides students with their classes in google classroom which will keep track of their task whether it’s being added or near the deadline and notify students when their work is near the due date via Discord.
This app also can create to-do lists for another purpose, so all the tasks is gather in a place so students can easily manage and observe
The reason that we chose this topic is because we want an application that can easily manage, show overview, flexible use for another purpose and keep track of tasks. For some tasks are in google classroom and some self tasks are in another app, it is hard to manage and observe overview, so this app is flexible enough for this problem.
Another one important reason is we want students to be able to keep track of their tasks whether tasks in google classroom or self task, and provide more frequent notification via Discord which another app doesn't do this like google classroom which only notify users 1 day before the due date.

## Background
Students have many things to do within deadlines, normally teachers take them to a to-do list or task board in Google Classroom for keeping track of them but sometimes that is not enough for example Google classroom will only notify users when the task is due the next day or an online to-do list which doesn't know what class you enrolled in so you have to create each class manually, moreover they have some other tasks that they have to do so our application is one of the alternative solutions for students to get rid of such annoyances for more flexible managing and observing.

## Table of content:
| Content |
| ------------------------------ |
| [Wiki Home](../../wiki/Home) |
| [Vision Statement](../../wiki/Vision%20Statement) |
| [Features list](../../wiki/Requirements) |
| [Installation Instruction](../../wiki/Installation%20Instruction) |

## Requirement before starting TO-DOZ

| Name | Required version(s) |
|------|---------------------|
| Python | 3.9 or Higher |
| Django | 4.1.1 |

### Getting Start

1. Clone the respository to your machine or PC.

    ```
   git clone https://github.com/Hamiz5401/TO-DOZ.git
    ```
2. Change directory to the local repository by typing this command.

    ```
   cd TO-DOZ
    ```
3. Install all require packages to your machine.

    ```
   pip install -r requirements.txt
    ```
4. Type this command to migrate the TO-DOZ database.

    ```
   py manage.py migrate
    ```
5. Running the server by this command.
    ```
   py manage.py runserver
    ```
    
## Iterations

[Iteration1](../../wiki/Iteration-1)

[Iteration2](../../wiki/Iteration-2)

[Iteration3](../../wiki/Iteration-3)

[Iteration4](../../wiki/Iteration-4)

[Iteration5](../../wiki/Iteration-5)

[Iteration6](../../wiki/Iteration-6)

[Iteration7](../../wiki/Iteration-7)
