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
