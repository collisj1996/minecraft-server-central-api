from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from msc.database import get_url
from msc.jobs.tasks import set_all_minecraft_versions
from msc.services.ping_service import poll_servers_async, update_servers_uptime

scheduler = BackgroundScheduler()
persisted_scheduler = BackgroundScheduler()

persisted_scheduler.add_jobstore("sqlalchemy", url=get_url())

scheduler.add_job(poll_servers_async, "interval", seconds=900)
scheduler.add_job(update_servers_uptime, "interval", seconds=3600)
scheduler.add_job(set_all_minecraft_versions, trigger=CronTrigger(hour=2))
