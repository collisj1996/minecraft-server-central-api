from fastapi import APIRouter
from msc.jobs.jobs import persisted_scheduler
from datetime import datetime, timedelta
from fastapi.requests import Request
from msc.services.auction_service import (
    start_payment_phase_task,
    populate_sponsored_servers_task,
)
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
