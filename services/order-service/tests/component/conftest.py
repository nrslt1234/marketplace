import importlib.util
from pathlib import Path
from unittest.mock import Mock

import confluent_kafka
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def order_service(monkeypatch):
    producer = Mock(spec=["produce", "flush"])
    producer.flush.return_value = 0

    # В main.py producer создаётся сразу при импорте.
    # Подменяем конструктор раньше, чем выполним этот файл.
    monkeypatch.setattr(confluent_kafka, "Producer", Mock(return_value=producer))

    path = Path(__file__).resolve().parents[2] / "main.py"
    spec = importlib.util.spec_from_file_location("order_service_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # При startup приложение запускает фоновый consumer.
    # В тесте его поток выполнит только пустую функцию, без Kafka и БД.
    monkeypatch.setattr(module, "run_consumer", lambda: None)
    return module, producer


@pytest.fixture
def client(order_service):
    module, _ = order_service
    with TestClient(module.app) as test_client:
        yield test_client
