from apscheduler.schedulers.background import BackgroundScheduler

from .tasks import poll_servers

scheduler = BackgroundScheduler()

# TODO: SET THIS TO 5 MINUTES
scheduler.add_job(poll_servers, "interval", seconds=20)
