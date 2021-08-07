from apscheduler.schedulers.background import BackgroundScheduler

import web_automation

scheduler = BackgroundScheduler()
scheduler.start()


def add_task(task):
    scheduler.add_job(
        lambda: web_automation.run_task(task),
        "date", 
        run_date=task.datetime
    )
