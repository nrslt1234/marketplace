from main import health_check


def test_health_check_returns_ok():
    assert health_check() == {"status": "ok"}


def test_health_check_has_only_status():
    assert set(health_check()) == {"status"}