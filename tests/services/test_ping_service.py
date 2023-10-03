import pytest
import freezegun
from datetime import datetime, timedelta

from msc.errors import NotFound, Unauthorized
from msc.models import Server, User, ServerHistory
from msc.services import ping_service, server_service


def test_poll_server_by_id_server_flagged_for_deletion(
    session,
    server_colcraft: Server,
):
    """Tests polling a server by id that is flagged for deletion"""

    server_service.delete_server(
        db=session,
        user_id=server_colcraft.user_id,
        server_id=server_colcraft.id,
    )

    with pytest.raises(NotFound):
        ping_service.poll_server_by_id(
            db=session,
            server_id=server_colcraft.id,
            user_id=server_colcraft.user_id,
        )


def test_poll_server_not_owned(session, server_colcraft: Server, user_alan: User):
    """Tests polling a server you do not own"""

    with pytest.raises(Unauthorized):
        ping_service.poll_server_by_id(
            db=session,
            server_id=server_colcraft.id,
            user_id=user_alan.id,
        )


def test_create_server_history_data_point(
    session,
    server_colcraft: Server,
):
    """Tests creating a server history data point"""

    assert (
        session.query(ServerHistory)
        .filter(ServerHistory.server_id == server_colcraft.id)
        .count()
        == 0
    )

    ping_service._create_server_history_data_point(
        db=session,
        server=server_colcraft,
        is_online=True,
        players=1,
    )

    data_point = (
        session.query(ServerHistory)
        .filter(
            ServerHistory.server_id == server_colcraft.id,
        )
        .one_or_none()
    )

    assert data_point
    assert data_point.server_id == server_colcraft.id
    assert data_point.is_online is True
    assert data_point.players == 1


def test_additional_data_points_within_one_minute(
    session,
    server_colcraft: Server,
):
    """Tests that additional data points made within 1 minute are not created"""

    ping_service._create_server_history_data_point(
        db=session,
        server=server_colcraft,
        is_online=True,
        players=1,
    )

    assert (
        session.query(ServerHistory)
        .filter(ServerHistory.server_id == server_colcraft.id)
        .count()
        == 1
    )

    ping_service._create_server_history_data_point(
        db=session,
        server=server_colcraft,
        is_online=True,
        players=1,
    )

    assert (
        session.query(ServerHistory)
        .filter(ServerHistory.server_id == server_colcraft.id)
        .count()
        == 1
    )


def test_create_data_points_for_different_servers_within_one_minute(
    session,
    server_colcraft: Server,
    server_hypixel: Server,
):
    """Tests that data points for different servers can be created within one minute"""

    ping_service._create_server_history_data_point(
        db=session,
        server=server_colcraft,
        is_online=True,
        players=1,
    )

    assert session.query(ServerHistory).count() == 1

    ping_service._create_server_history_data_point(
        db=session,
        server=server_hypixel,
        is_online=True,
        players=1,
    )

    assert session.query(ServerHistory).count() == 2


def test_can_create_another_data_point_after_ten_minutes(
    session,
    server_colcraft: Server,
):
    """Tests that multiple data points can be created after one minute"""

    now = datetime.utcnow()

    with freezegun.freeze_time(now):
        ping_service._create_server_history_data_point(
            db=session,
            server=server_colcraft,
            is_online=True,
            players=1,
        )

    assert (
        session.query(ServerHistory)
        .filter(ServerHistory.server_id == server_colcraft.id)
        .count()
        == 1
    )

    with freezegun.freeze_time(now + timedelta(seconds=59)):
        ping_service._create_server_history_data_point(
            db=session,
            server=server_colcraft,
            is_online=False,
            players=2,
        )

    assert (
        session.query(ServerHistory)
        .filter(ServerHistory.server_id == server_colcraft.id)
        .count()
        == 1
    )

    with freezegun.freeze_time(now + timedelta(minutes=1, seconds=1)):
        ping_service._create_server_history_data_point(
            db=session,
            server=server_colcraft,
            is_online=False,
            players=2,
        )

    assert (
        session.query(ServerHistory)
        .filter(ServerHistory.server_id == server_colcraft.id)
        .count()
        == 2
    )


def test_update_server_uptime(
    session,
    server_colcraft: Server,
    server_colcraft_history,
):
    """Tests updating a server's uptime"""

    assert server_colcraft.uptime == 100.0  # default value

    ping_service._update_server_uptime(
        db=session,
        server=server_colcraft,
    )

    # get the server again from the database
    server_colcraft = (
        session.query(Server).filter(Server.id == server_colcraft.id).one_or_none()
    )

    assert server_colcraft.uptime == 95.65
