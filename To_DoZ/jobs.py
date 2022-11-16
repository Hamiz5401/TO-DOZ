import datetime
from .scheduler import scheduler
from discordwebhook import Discord
from apscheduler.triggers.date import DateTrigger
from .models import Task, Discord_url
from django.utils import timezone


def add_noti_discord(task: Task, user, time):
    if Discord_url.objects.filter(user=user).exists():
        dis = Discord_url.objects.filter(user=user)
        dis_url = dis[0]
        discord = Discord(url=dis_url)
        discord.post(content=f"{task.title} has {time} hour left before deadline.")


def add_job(task: Task, user):
    if task.deadline is not None:
        for time in [1, 6, 24]:
            time_to_call = task.deadline - timezone.timedelta(hours=time)
            if time_to_call > (timezone.localtime()):
                noti = scheduler.add_job(func=add_noti_discord,
                                         trigger=DateTrigger(run_date=time_to_call),
                                         replace_existing=True,
                                         max_instances=1,
                                         id=f"Noti - {task.pk} - {task.title} - {time}",
                                         args=[task, user, time])
                print(f"{task.title} has set noti to trigger on {noti.next_run_time}")


def clear_job(task: Task):
    for time in [1, 6, 24]:
        job_id = f"Noti - {task.pk} - {task.title} - {time}"
        if scheduler.get_job(job_id) is not None:
            scheduler.remove_job(job_id)
            print(f"{task.title} has deleted it schedule.")

