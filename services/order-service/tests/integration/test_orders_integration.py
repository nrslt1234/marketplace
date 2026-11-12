import json
import os
import uuid
from decimal import Decimal
from time import monotonic, sleep
from uuid import UUID

import pytest
from psycopg2.errors import UndefinedTable


def wait_for_order(connection, order_id, timeout=20):
    deadline = monotonic() + timeout
    with connection.cursor() as cursor:
        while monotonic() < deadline:
            try:
                cursor.execute(
                    "SELECT customer_id, total, payload FROM orders WHERE order_id = %s",
                    (order_id,),
                )
                row = cursor.fetchone()
                if row is not None:
                    return row
            except UndefinedTable:
                # При первом запуске consumer сам создаёт таблицу orders.
                pass
            sleep(0.2)

    pytest.fail(f"Заказ {order_id} не появился в PostgreSQL за {timeout} с")


@pytest.mark.parametrize(
    "customer_id, items, expected_total",
    [
        pytest.param(
            7,
            [{"product_id": 10, "quantity": 2, "price": 125.5}],
            "251.00",
            id="one-item",
        ),
        pytest.param(
            8,
            [
                {"product_id": 10, "quantity": 2, "price": 125.5},
                {"product_id": 20, "quantity": 1, "price": 49.9},
            ],
            "300.90",
            id="two-items",
        ),
    ],
)
def test_order_is_saved_after_kafka_delivery(
    client, db_connection, customer_id, items, expected_total
):
    # Arrange
    payload = {"customer_id": customer_id, "items": items}

    # Act
    response = client.post("/orders", json=payload)

    # Assert: HTTP-контракт
    assert response.status_code == 201, response.text
    body = response.json()
    order_id = str(UUID(body["order_id"]))
    assert body["status"] == "created"
    assert Decimal(str(body["total"])) == Decimal(expected_total)

    # Assert: состояние после обработки события
    saved_customer_id, saved_total, event = wait_for_order(db_connection, order_id)
    assert saved_customer_id == customer_id
    assert saved_total == Decimal(expected_total)
    assert event == {
        "event_type": "order.created",
        "order_id": order_id,
        "customer_id": customer_id,
        "total": body["total"],
        "items": items,
    }






# Задача № 1
# В одном тесте отправь два корректных запроса с разными покупателями.
# Проверь оба статуса, разные order_id и две записи в PostgreSQL. Для каждой записи проверь покупателя и сумму, чтобы поймать перепутанные события.

def test_two_orders_are_saved_independently(client, db_connection):
    first_payload = {
        "customer_id": 7,
        "items": [
            {"product_id": 10, "quantity": 2, "price": 125.5}
        ],
    }

    second_payload = {
        "customer_id": 8,
        "items": [
            {"product_id": 20, "quantity": 1, "price": 300.0}
        ],
    }

    first_response = client.post("/orders", json=first_payload)
    second_response = client.post("/orders", json=second_payload)


    assert first_response.status_code == 201, first_response.text
    assert second_response.status_code == 201, second_response.text

    first_body = first_response.json()
    second_body = second_response.json()

    assert first_body["status"] == "created"
    assert second_body["status"] == "created"

    first_id = str(UUID(first_body["order_id"]))
    second_id = str(UUID(second_body["order_id"]))

    assert first_id != second_id

    first_saved = wait_for_order(db_connection, first_id)
    second_saved = wait_for_order(db_connection, second_id)

    assert first_saved[0] == 7
    assert first_saved[1] == Decimal("251.00")

    assert second_saved[0] == 8
    assert second_saved[1] == Decimal("300.00")












from confluent_kafka import Producer


def test_duplicate_order_event_is_ignored(client, db_connection):
    payload = {
        "customer_id": 7,
        "items": [
            {"product_id": 10, "quantity": 2, "price": 250.0}
        ],
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 201, response.text

    body = response.json()

    order_id = str(UUID(body["order_id"]))

    # Проверяем, что первоначальный заказ сохранился
    first_saved = wait_for_order(db_connection, order_id)

    assert first_saved[0] == 7
    assert first_saved[1] == Decimal("500.00")


    producer = Producer({
        "bootstrap.servers": os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "kafka:19092"
        ),
        "client.id": "integration-test",
    })

    topic = os.getenv(
        "KAFKA_ORDERS_TOPIC", "orders.integration"
    )

    delivery_errors = []

    def send_event(event):
        producer.produce(
            topic,
            key=event["order_id"],
            value=json.dumps(event).encode("utf-8"),
            partition=0,
            on_delivery=lambda err, msg: (
                delivery_errors.append(str(err)) if err else None
            ),
        )

        remaining = producer.flush(10)

        assert remaining == 0, "Kafka не доставила сообщение"
        assert not delivery_errors, delivery_errors

    # 3. Отправляем повторное событие
    # UUID тот же, но покупатель и сумма другие
    duplicate_event = {
        "order_id": order_id,
        "customer_id": 99,
        "total": 9999.00,
    }

    send_event(duplicate_event)

    # 4. Отправляем контрольное событие
    # У него новый UUID
    control_id = str(uuid.uuid4())

    control_event = {
        "order_id": control_id,
        "customer_id": 15,
        "total": 100.00,
    }

    send_event(control_event)

    # 5. Ждём, пока Consumer обработает контрольное событие
    control_saved = wait_for_order(db_connection, control_id)

    assert control_saved[0] == 15
    assert control_saved[1] == Decimal("100.00")

    # 6. Проверяем, что первоначальный заказ не изменился
    first_saved = wait_for_order(db_connection, order_id)

    assert first_saved[0] == 7
    assert first_saved[1] == Decimal("500.00")

    # 7. Проверяем, что первоначальный заказ существует ровно один раз
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE order_id = %s
            """,
            (order_id,),
        )

        count = cursor.fetchone()[0]

    assert count == 1
