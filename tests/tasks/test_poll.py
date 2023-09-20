from msc.jobs.tasks import poll_servers



def test_poll_servers(session, server_colcraft):
    """Test poll servers task function"""

    poll_servers()