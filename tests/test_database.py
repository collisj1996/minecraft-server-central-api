import os


def test_database_exists():
    assert os.path.exists("data.db")
