from apscheduler.schedulers.background import BackgroundScheduler

from msc.services.ping_service import poll_servers_async

scheduler = BackgroundScheduler()

scheduler.add_job(poll_servers_async, "interval", seconds=900)
