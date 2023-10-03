from apscheduler.schedulers.background import BackgroundScheduler

from msc.services.ping_service import poll_servers_async, update_servers_uptime

scheduler = BackgroundScheduler()

scheduler.add_job(poll_servers_async, "interval", seconds=900)
scheduler.add_job(update_servers_uptime, "interval", seconds=3600)
