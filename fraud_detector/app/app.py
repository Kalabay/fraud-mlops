import json
import os
import sys
from pathlib import Path

import pandas as pd
from confluent_kafka import Consumer, Producer, KafkaError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from preprocessing import load_train_data, run_preproc
from scorer import make_pred


def main():
    train = load_train_data()
    consumer = Consumer({
        "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
        "group.id": "ml-scorer",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False
    })
    producer = Producer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")})
    consumer.subscribe([os.getenv("KAFKA_TRANSACTIONS_TOPIC", "transactions")])
    try:
        while True:
            msg = consumer.poll(1)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise RuntimeError(msg.error())
            row = json.loads(msg.value())
            data = pd.DataFrame([row["data"]])
            result = make_pred(run_preproc(train, data)).iloc[0]
            print("score ready", flush=True)
            score = {"transaction_id": str(row["transaction_id"]), "score": float(result["score"]), "fraud_flag": int(result["fraud_flag"])}
            errors = []
            producer.produce(
                os.getenv("KAFKA_SCORING_TOPIC", "scores"),
                key=score["transaction_id"],
                value=json.dumps(score),
                on_delivery=lambda err, message: errors.append(err) if err else None
            )
            if producer.flush(30) or errors:
                raise RuntimeError("kafka send failed")
            consumer.commit(message=msg, asynchronous=False)
    finally:
        consumer.close()
        producer.flush(5)


if __name__ == "__main__":
    main()
