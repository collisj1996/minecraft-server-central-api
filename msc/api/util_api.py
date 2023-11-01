from fastapi import APIRouter
from msc.jobs.jobs import persisted_scheduler
from datetime import datetime, timedelta
from fastapi.requests import Request
from msc.services.auction_service import (
    start_payment_phase_task,
    populate_sponsored_servers_task,
)
from msc.services.email_service import send_email as send_email_
from msc.utils.api_utils import admin_required

router = APIRouter()


@router.get("/health")
def health():
    return {"message": "healthy"}


@router.post("/test/task_pay_phase")
@admin_required
def task_pay_phase(request: Request):
    persisted_scheduler.add_job(
        start_payment_phase_task,
        "date",
        run_date=datetime.utcnow() + timedelta(seconds=20),
    )


@router.post("/test/populate_sponsored_slots")
@admin_required
def populate_sponsored_slots(request: Request):
    persisted_scheduler.add_job(
        populate_sponsored_servers_task,
        "date",
        run_date=datetime.utcnow() + timedelta(seconds=20),
    )


@router.post("/test/send_email")
@admin_required
def send_email(request: Request, body: dict) -> str:
    send_email_(
        subject=body.get("subject"),
        recipient=body.get("recipient"),
        template=body.get("template"),
        params=body.get("params"),
    )
    return "success"
