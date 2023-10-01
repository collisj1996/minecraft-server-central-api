import pytest

from msc.errors import NotFound, Unauthorized
from msc.models import Server, User
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
