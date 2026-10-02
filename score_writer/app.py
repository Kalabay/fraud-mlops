import json
import os

import psycopg2
from confluent_kafka import Consumer, KafkaError


def save_score(conn, row):
    with conn:
        with conn.cursor() as cur:
            query = "INSERT INTO scores (transaction_id, score, fraud_flag) VALUES (%s, %s, %s) ON CONFLICT (transaction_id) DO NOTHING"
            values = (row["transaction_id"], row["score"], row["fraud_flag"])
            cur.execute(query, values)


def main():
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    consumer = Consumer({
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        "group.id": "score-writer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False
    })
    consumer.subscribe([os.getenv("KAFKA_SCORING_TOPIC", "scores")])
    try:
        while True:
            msg = consumer.poll(1)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise RuntimeError(msg.error())
            save_score(conn, json.loads(msg.value()))
            print("result saved", flush=True)
            consumer.commit(message=msg, asynchronous=False)
    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    main()
