import json
from uuid import UUID

import pytest


def test_create_order_returns_201_and_publishes_event(client, order_service):
    # Arrange
    module, producer = order_service
    payload = {
        "customer_id": 7,
        "items": [
            {"product_id": 10, "quantity": 2, "price": 125.5},
            {"product_id": 20, "quantity": 1, "price": 49.9},
        ],
    }

    # Act
    response = client.post("/orders", json=payload)

    # Assert: внешний контракт API
    assert response.status_code == 201
    body = response.json()
    assert body == {
        "order_id": body["order_id"],
        "status": "created",
        "total": 300.9,
    }
    assert str(UUID(body["order_id"])) == body["order_id"]

    # Assert: контракт сообщения на границе с Kafka
    producer.produce.assert_called_once()
    args, kwargs = producer.produce.call_args
    assert args == (module.TOPIC,)
    assert kwargs["key"] == body["order_id"]
    assert isinstance(kwargs["value"], bytes)
    event = json.loads(kwargs["value"].decode("utf-8"))
    assert event == {
        "event_type": "order.created",
        "order_id": body["order_id"],
        "total": 300.9,
        **payload,
    }
    producer.flush.assert_called_once_with(10)


@pytest.mark.parametrize(
    "items, expected_total",
    [
        ([{"product_id": 1, "quantity": 1, "price": 100}], 100),
        ([{"product_id": 1, "quantity": 3, "price": 19.99}], 59.97),
        (
            [
                {"product_id": 1, "quantity": 2, "price": 10.25},
                {"product_id": 2, "quantity": 3, "price": 4.5},
            ],
            34,
        ),
    ],
)
def test_order_total(client, order_service, items, expected_total):
    module, producer = order_service
    response = client.post("/orders", json={"customer_id": 7, "items": items})

    assert response.status_code == 201
    assert response.json()["total"] == expected_total
    producer.produce.assert_called_once()
    event = json.loads(producer.produce.call_args.kwargs["value"])
    assert event["total"] == expected_total
    assert event["items"] == items
    assert producer.produce.call_args.args == (module.TOPIC,)


@pytest.mark.parametrize(
    "payload, error_location",
    [
        ({"items": []}, ["body", "customer_id"]),
        ({"customer_id": 7}, ["body", "items"]),
        (
            {"customer_id": 7, "items": [
                {"product_id": 1, "quantity": "many", "price": 10}
            ]},
            ["body", "items", 0, "quantity"],
        ),
        (
            {"customer_id": 7, "items": [
                {"product_id": 1, "quantity": 1}
            ]},
            ["body", "items", 0, "price"],
        ),
    ],
)
def test_invalid_order_returns_422_without_publishing(
    client, order_service, payload, error_location
):
    _, producer = order_service
    response = client.post("/orders", json=payload)

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"] == error_location for error in errors)
    producer.produce.assert_not_called()
    producer.flush.assert_not_called()


def test_produce_error_returns_503(client, order_service):
    _, producer = order_service
    producer.produce.side_effect = RuntimeError("Kafka is unavailable")

    response = client.post("/orders", json={
        "customer_id": 7,
        "items": [{"product_id": 1, "quantity": 1, "price": 100}],
    })

    assert response.status_code == 503
    assert response.json() == {"detail": "Kafka unavailable"}
    producer.produce.assert_called_once()
    producer.flush.assert_not_called()


def test_pending_messages_after_flush_return_503(client, order_service):
    _, producer = order_service
    producer.flush.return_value = 1

    response = client.post("/orders", json={
        "customer_id": 7,
        "items": [{"product_id": 1, "quantity": 1, "price": 100}],
    })

    assert response.status_code == 503
    assert response.json() == {"detail": "Kafka unavailable"}
    producer.produce.assert_called_once()
    producer.flush.assert_called_once_with(10)
