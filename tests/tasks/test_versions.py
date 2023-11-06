from msc.jobs.tasks import _get_minecraft_versions, set_all_minecraft_versions
from msc.models import MinecraftVersion
from msc.services.version_service import process_version_from_ping


def test_get_minecraft_versions():
    versions = _get_minecraft_versions()
    assert len(versions.get("versions")) > 700


def test_update_all_minecraft_versions(session):
    set_all_minecraft_versions()
    assert session.query(MinecraftVersion).count() > 700


def test_process_version_from_ping(session):
    versions_to_process = [
        "BungeeCord 1.8.x-1.20.x",
        "Waterfall 1.8.x, 1.9.x, 1.10.x, 1.11.x, 1.12.x, 1.13.x, 1.14.x, 1.15.x, 1.16.x, 1.17.x, 1.18.x, 1.19.x, 1.20.x",
        "Escanor",
        "FlameCord 1.7-1.19.2",
        "Waterfall 1.18.x,1.19.0,1.20.x",
        "§11.16.5 -> 1.20.1",
        "XCord 1.7.x, 1.8.x, 1.9.x, 1.10.x, 1.11.x, 1.12.x, 1.13.x, 1.14.x, 1.15.x, 1.16.x, 1.17.x, 1.18.x, 1.19.x, 1.20.x",
        "Paper 1.20.1",
        "§f",
        "1.2.3",
        "12",
        "§fÚnete! §a➤                                                                         §712/80",
        "Paper 1.19.4",
        "Gods-Realm 1.8-1.20.2",
        "1.6.7",
        "Magma 1.18.2",
        "1.20+",
        "Mohist 1.12.2",
        "Velocity 1.7.2-1.20.1",
        "Paper 1.20.2",
        "Velocity 1.7.2-1.20.2",
        "1.16.5",
        "Iridium Network 1.20.1",
    ]

    processed_versions = []

    for raw_version in versions_to_process:
        processed_versions.append(
            process_version_from_ping(
                db=session,
                raw_version=raw_version,
            ),
        )

    print(1)
