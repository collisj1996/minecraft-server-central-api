from msc.jobs.tasks import _get_minecraft_versions, set_all_minecraft_versions
from msc.models import MinecraftVersion


def test_get_minecraft_versions():
    versions = _get_minecraft_versions()
    assert len(versions.get("versions")) > 700


def test_update_all_minecraft_versions(session):
    set_all_minecraft_versions()
    assert session.query(MinecraftVersion).count() > 700
