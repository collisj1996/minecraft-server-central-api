import logging

from fastapi import APIRouter, Body

from msc.migrations.db_migration import run_migrations
from msc.utils.db_utils import validate_database

logger = logging.getLogger("msc_db_log")

router = APIRouter()


@router.post("/migration/downgrade_latest")
def downgrade_latest():
    return run_migrations(upgrade=False)


@router.post("/migration/downgrade_to_version")
def downgrade_to_version(body: dict = Body(...)):
    return run_migrations(upgrade=False, downgrade_target=body.version)


@router.post("/migration/upgrade")
def upgrade():
    return run_migrations()
