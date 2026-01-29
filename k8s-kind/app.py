import os
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Students will need to figure out how to pass these via Kubernetes Env Vars
DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST
    )

class Record(BaseModel):
    message: str

@app.on_event("startup")
def setup_db():
    """Ensures the table exists on startup."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS logs (id SERIAL PRIMARY KEY, message TEXT);")
    conn.commit()
    cur.close()
    conn.close()

@app.get("/health")
def health():
    return {"status": "up"}

@app.post("/write")
def write_to_db(record: Record):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO logs (message) VALUES (%s)", (record.message,))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "inserted": record.message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))