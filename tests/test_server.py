from msc.models import Server


def test_create_server(session):
    assert session.query(Server).count() == 0

    server = Server(
        name="My Server",
        description="My Server Description",
        ip_address="192.168.1.100",
        port=8080,
        country_code="GB",
        minecraft_version="1.16.5",
        votifier_ip_address=None,
        votifier_port=None,
        votifier_key=None,
        website="https://www.myserver.com",
        discord="https://discord.gg/myserver",
    )

    # You can then save the server to a database session
    session.add(server)
    session.commit()

    assert session.query(Server).count() == 1
