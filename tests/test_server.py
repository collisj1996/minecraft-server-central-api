from msc.models import Server

def test_create_server(session):

    assert session.query(Server).count() == 0

    server = Server(
        name="My Server",
        description="My Server Description",
        ip_address="192.168.1.100",
        port=8080,
        website="https://www.myserver.com",
        created_at="2021-01-01 00:00:00",
        updated_at="2021-01-01 00:00:00",
    )

    # You can then save the server to a database session
    session.add(server)
    session.commit()

    assert session.query(Server).count() == 1
