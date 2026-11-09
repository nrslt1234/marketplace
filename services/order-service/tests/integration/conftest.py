import os

import httpx
import psycopg2
import pytest


@pytest.fixture
def client():
    with httpx.Client(base_url=os.environ["TEST_BASE_URL"], timeout=15) as client:
        yield client


@pytest.fixture
def db_connection():
    dsn = os.environ["TEST_DATABASE_URL"]
    assert psycopg2.extensions.parse_dsn(dsn)["dbname"] == "marketplace_integration"
    connection = psycopg2.connect(dsn, connect_timeout=5)
    connection.autocommit = True
    try:
        yield connection
    finally:
        connection.close()
