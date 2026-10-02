import pandas as pd
import psycopg2


def load_results(url):
    conn = psycopg2.connect(url, connect_timeout=5)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT transaction_id, score, fraud_flag, created_at FROM scores WHERE fraud_flag = 1 ORDER BY id DESC LIMIT 10")
            fraud = pd.DataFrame(cur.fetchall(), columns=["transaction_id", "score", "fraud_flag", "created_at"])
            cur.execute("SELECT score FROM scores ORDER BY id DESC LIMIT 100")
            scores = pd.DataFrame(cur.fetchall(), columns=["score"])
        return fraud, scores
    finally:
        conn.close()
