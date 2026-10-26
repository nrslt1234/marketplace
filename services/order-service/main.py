import json
import os
import threading
import uuid

import psycopg2
from confluent_kafka import Consumer, Producer
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

KAFKA = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:19092")
TOPIC = os.getenv("KAFKA_ORDERS_TOPIC", "orders.created")
DB_URL = os.getenv("DATABASE_URL", "postgresql://app_user:app_pass@db:5432/app_db").replace("+psycopg2", "")

producer = Producer({"bootstrap.servers": KAFKA, "client.id": "order-service"})


def run_consumer():
    consumer = Consumer({
        "bootstrap.servers": KAFKA,
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
    finally:
        consumer.close()
        db.close()


@app.on_event("startup")
def start_consumer():
    threading.Thread(target=run_consumer, daemon=True).start()


class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class Order(BaseModel):
    customer_id: int
    items: list[OrderItem]


@app.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order: Order) -> dict:
    order_id = str(uuid.uuid4())
    total = round(sum(item.price * item.quantity for item in order.items), 2)
    event = {"event_type": "order.created", "order_id": order_id, "total": total, **order.model_dump()}
    try:
        producer.produce(TOPIC, key=order_id, value=json.dumps(event).encode())
        if producer.flush(10):
            raise RuntimeError("event not delivered")
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Kafka unavailable") from exc
    return {"order_id": order_id, "status": "created", "total": total}
