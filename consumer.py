import json
import os

import psycopg2
from confluent_kafka import Consumer

DB_URL = os.getenv("DATABASE_URL", "postgresql://app_user:app_pass@db:5432/app_db").replace("+psycopg2", "")
TOPIC = os.getenv("KAFKA_ORDERS_TOPIC", "orders.created")


def run_consumer():
    consumer = Consumer({
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:19092"),
        "group.id": "order-service",
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe([TOPIC])

    db = psycopg2.connect(DB_URL)
    db.autocommit = True
    with db.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id uuid PRIMARY KEY,
                customer_id bigint NOT NULL,
                total numeric(12, 2) NOT NULL,
                payload jsonb NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now()
            )
        """)

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("Kafka error:", msg.error())
                continue
            order = json.loads(msg.value())
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO orders (order_id, customer_id, total, payload) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                    (order["order_id"], order["customer_id"], order["total"], json.dumps(order)),
                )
            print("Сохранён заказ:", order["order_id"], "сумма:", order["total"])
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
        db.close()
