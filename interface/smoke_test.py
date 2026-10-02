import json
import os
import time
import uuid

import pandas as pd
import psycopg2
from kafka import KafkaProducer


def main():
    data = pd.read_csv('/app/test_data/test.csv', nrows=10)
    producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA_BROKERS', 'kafka:9092'), value_serializer=lambda row: json.dumps(row).encode())
    ids = []
    for row in json.loads(data.to_json(orient='records')):
        name = str(uuid.uuid4())
        ids.append(name)
        producer.send('transactions', {'transaction_id': name, 'data': row}).get(timeout=30)
    producer.flush()
    producer.close()
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    try:
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            with conn.cursor() as cur:
                cur.execute('SELECT transaction_id, score, fraud_flag FROM scores WHERE transaction_id = ANY(%s)', (ids,))
                rows = cur.fetchall()
            conn.commit()
            if len(rows) == len(ids):
                assert all(0 <= row[1] <= 1 and row[2] in (0, 1) for row in rows)
                print('test ok: 10 results saved')
                return
            time.sleep(2)
        raise RuntimeError(f'test failed: {len(rows)}/{len(ids)} results saved')
    finally:
        conn.close()


if __name__ == '__main__':
    main()
