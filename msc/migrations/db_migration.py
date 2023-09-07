import os
import logging

from alembic import command
from alembic.config import Config

from msc.utils.db_utils import validate_database

logger = logging.getLogger("msc_db_log")


def run_migrations(alembic_dir_path=None, upgrade=True, downgrade_target=None,):
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", ".."),
    )

    if not alembic_dir_path:
        alembic_dir_path = os.path.join(base_dir, "alembic")

    alembic_cgf = Config(os.path.join(base_dir, "alembic.ini"))
    alembic_cgf.set_main_option("script_location", alembic_dir_path)

    if upgrade:
        command.upgrade(alembic_cgf, "head")
        logger.info("Upgrade complete")
        return "alembic upgrade complete"
    else:
        if downgrade_target:
            command.downgrade(config=alembic_cgf, revision=downgrade_target)
            logger.info(f"Downgrade complete to specific revision {downgrade_target}")
            return f"alembic downgrade complete to {downgrade_target}"
        command.downgrade(alembic_cgf, "-1")
        logger.info("Downgrade complete to previous revision")
        return "alembic downgrade complete to previous revision"

if __name__ == "__main__":
    validate_database()
    run_migrations()