import datetime
from aps_scheduler import scheduler
from discordwebhook import Discord
from apscheduler.triggers.date import DateTrigger
from .models import Task


def add_noti_discord(task: Task):
    discord = Discord(
        url="https://discord.com/api/webhooks/1039515198840651797/0phytK41IJoudw-YNU"
            "-tf3sDa4_21wv75QC0hQ3FTYM0STrMWpXOJdqlKSkq4zb4pnAC")
    discord.post(content=f"{task.title} has 1 hour left before deadline.")


def add_job(task: Task):
    time_to_call = task.deadline - datetime.timedelta(hours=1)
    if time_to_call > datetime.datetime.now():
        noti = scheduler.add_job(func=add_noti_discord(task),
                                 trigger=DateTrigger(run_date=time_to_call),
                                 replace_existing=True,
                                 max_instances=1,
                                 id=f"Noti - {task.pk} - {task.title}")
        print(f"{task.title} has set noti to trigger on {noti.next_run_time}")
