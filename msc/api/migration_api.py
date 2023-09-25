import logging

from fastapi import APIRouter, Body
from starlette.requests import Request

from msc.migrations.db_migration import run_migrations
from msc.utils.api_utils import admin_required

logger = logging.getLogger("msc_db_log")

router = APIRouter()


@router.post("/migration/downgrade_latest")
@admin_required
def downgrade_latest(request: Request):
    return run_migrations(upgrade=False)


@router.post("/migration/downgrade_to_version")
@admin_required
def downgrade_to_version(request: Request, body: dict = Body(...)):
    return run_migrations(upgrade=False, downgrade_target=body.version)


@router.post("/migration/upgrade")
@admin_required
def upgrade(request: Request):
    return run_migrations()
